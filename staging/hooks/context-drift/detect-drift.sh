#!/usr/bin/env bash
# Context Drift Detector — SessionStart hook
# Detects when code evolution has outpaced documentation.
# Fires at most once per week per repo. Informational only (always exits 0).
#
# What counts as drift:
#   1. Code:doc ratio > 10:1 by files changed (not zero-check — proportional)
#   2. CLAUDE.md stale (30+ days) while code is actively changing
#   3. Specific high-churn directories with zero doc coverage
#
# Anti-noise:
#   - Fires once per 7 days per repo (state file tracks last warning)
#   - Config files (package.json, tsconfig, Dockerfile) are NOT documentation
#   - Actionable output: names the drifted directories, not just "update docs"

set -euo pipefail
trap 'exit 0' ERR

# --- Configuration ---
LOOKBACK_DAYS="${DRIFT_LOOKBACK_DAYS:-14}"
RATIO_THRESHOLD="${DRIFT_RATIO_THRESHOLD:-10}"    # code:doc file ratio to trigger
STALE_DAYS="${DRIFT_STALE_DAYS:-30}"
COOLDOWN_DAYS="${DRIFT_COOLDOWN_DAYS:-7}"          # suppress repeat warnings
CHURN_THRESHOLD="${DRIFT_CHURN_THRESHOLD:-5}"      # files in a dir to flag it
STATE_DIR="${HOME}/.claude/hooks/context-drift/state"

# Validate thresholds are positive integers
for var in LOOKBACK_DAYS RATIO_THRESHOLD STALE_DAYS COOLDOWN_DAYS CHURN_THRESHOLD; do
  if ! [[ "${!var}" =~ ^[0-9]+$ ]]; then
    exit 0
  fi
done

# Cap lookback
if [ "$LOOKBACK_DAYS" -gt 90 ]; then
  LOOKBACK_DAYS=90
fi

# --- Early exits ---

# Not a git repo
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  exit 0
fi

# Shallow clone — unreliable history
if [ -f "$(git rev-parse --git-dir)/shallow" ]; then
  exit 0
fi

# Empty repo (no commits)
if ! git rev-parse HEAD >/dev/null 2>&1; then
  exit 0
fi

# --- Cooldown check ---
# One warning per repo per COOLDOWN_DAYS period

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "$REPO_ROOT" ]; then
  exit 0
fi

mkdir -p "$STATE_DIR"
# Use repo path hash as state file name (avoid path chars in filename)
REPO_HASH=$(printf '%s' "$REPO_ROOT" | shasum -a 256 | cut -c1-12)
STATE_FILE="${STATE_DIR}/${REPO_HASH}.last-warned"

if [ -f "$STATE_FILE" ]; then
  LAST_WARNED=$(cat "$STATE_FILE" 2>/dev/null || echo "0")
  NOW=$(date +%s)
  ELAPSED_DAYS=$(( (NOW - LAST_WARNED) / 86400 ))
  if [ "$ELAPSED_DAYS" -lt "$COOLDOWN_DAYS" ]; then
    exit 0  # Already warned recently, stay quiet
  fi
fi

# --- Single-pass: gather numstat ---

SINCE="${LOOKBACK_DAYS} days ago"
NUMSTAT_ALL=$(git log --since="$SINCE" --numstat --pretty=format: | grep -v '^$' || true)

if [ -z "$NUMSTAT_ALL" ]; then
  exit 0
fi

CHANGED_FILES=$(echo "$NUMSTAT_ALL" | awk '{print $3}' | sort -u)

# --- Categorize files (strict separation) ---

# Code: actual source files
CODE_EXTENSIONS='\.ts$|\.tsx$|\.js$|\.jsx$|\.py$|\.go$|\.rs$|\.java$|\.swift$|\.rb$|\.php$|\.css$|\.scss$'

# Documentation: ONLY actual docs, not config
DOC_EXTENSIONS='\.md$|\.mdx$|\.rst$|\.txt$|CHANGELOG|CONTRIBUTING'

# Config: explicitly separate (does NOT suppress drift warnings)
# CONFIG_EXTENSIONS='package\.json$|tsconfig|Dockerfile|docker-compose|\.env|\.eslint|\.prettier'

CODE_FILES=$(echo "$CHANGED_FILES" | grep -E "$CODE_EXTENSIONS" || true)
DOC_FILES=$(echo "$CHANGED_FILES" | grep -E "$DOC_EXTENSIONS" || true)

CODE_FILE_COUNT=0
if [ -n "$CODE_FILES" ]; then
  CODE_FILE_COUNT=$(printf '%s\n' "$CODE_FILES" | grep -c .)
fi

DOC_FILE_COUNT=0
if [ -n "$DOC_FILES" ]; then
  DOC_FILE_COUNT=$(printf '%s\n' "$DOC_FILES" | grep -c .)
fi

# Not enough code activity to care
if [ "$CODE_FILE_COUNT" -lt 5 ]; then
  exit 0
fi

# --- Count code lines changed ---

CODE_LINES_CHANGED=0
CODE_NUMSTAT=$(echo "$NUMSTAT_ALL" | grep -E "$CODE_EXTENSIONS" || true)
if [ -n "$CODE_NUMSTAT" ]; then
  CODE_LINES_CHANGED=$(echo "$CODE_NUMSTAT" | awk '{ if ($1 != "-" && $2 != "-") sum += $1 + $2 } END { print sum+0 }')
fi

# --- Detect drift (ratio-based, not binary) ---

WARNINGS=""
SHOULD_WARN=false

# Check 1: Code-to-doc ratio
if [ "$DOC_FILE_COUNT" -eq 0 ]; then
  # Zero docs is always a flag if code activity is significant
  WARNINGS="${WARNINGS}[Context Drift] ${CODE_FILE_COUNT} code files changed (${CODE_LINES_CHANGED} lines) in the last ${LOOKBACK_DAYS} days with zero documentation updates.\n"
  SHOULD_WARN=true
elif [ "$DOC_FILE_COUNT" -gt 0 ]; then
  RATIO=$((CODE_FILE_COUNT / DOC_FILE_COUNT))
  if [ "$RATIO" -ge "$RATIO_THRESHOLD" ]; then
    WARNINGS="${WARNINGS}[Context Drift] Code:doc ratio is ${RATIO}:1 (${CODE_FILE_COUNT} code files vs ${DOC_FILE_COUNT} doc files in ${LOOKBACK_DAYS} days).\n"
    SHOULD_WARN=true
  fi
fi

# Check 2: CLAUDE.md staleness
CLAUDE_MD=""
if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
  CLAUDE_MD="$REPO_ROOT/CLAUDE.md"
fi

if [ -n "$CLAUDE_MD" ]; then
  LAST_MODIFIED=$(git log -1 --format=%ct -- "$CLAUDE_MD" 2>/dev/null || echo "0")
  NOW=$(date +%s)
  DAYS_SINCE_UPDATE=$(( (NOW - LAST_MODIFIED) / 86400 ))

  if [ "$DAYS_SINCE_UPDATE" -ge "$STALE_DAYS" ]; then
    WARNINGS="${WARNINGS}[Context Drift] CLAUDE.md last updated ${DAYS_SINCE_UPDATE} days ago.\n"
    SHOULD_WARN=true
  fi
fi

# Check 3: High-churn directories with no doc coverage
# Find directories with 5+ code file changes, check if any .md exists nearby
if [ -n "$CODE_FILES" ]; then
  HOT_DIRS=$(printf '%s\n' "$CODE_FILES" | \
    sed -E 's|/[^/]+$||' | \
    sort | uniq -c | sort -rn | \
    awk -v thresh="$CHURN_THRESHOLD" '$1 >= thresh {print $1, $2}')

  if [ -n "$HOT_DIRS" ]; then
    UNDOCUMENTED_DIRS=""
    while read -r count dir; do
      [ -z "$dir" ] && continue
      # Check if any .md file exists in or adjacent to this directory
      # Directory may not exist on disk (deleted in later commits) — guard with -d
      if [ ! -d "$REPO_ROOT/$dir" ]; then
        UNDOCUMENTED_DIRS="${UNDOCUMENTED_DIRS}  - ${dir}/ (${count} files changed)\n"
        continue
      fi
      HAS_DOCS=$(find "$REPO_ROOT/$dir" -maxdepth 1 -name "*.md" -type f 2>/dev/null | head -1)
      if [ -z "$HAS_DOCS" ]; then
        UNDOCUMENTED_DIRS="${UNDOCUMENTED_DIRS}  - ${dir}/ (${count} files changed)\n"
      fi
    done <<< "$HOT_DIRS"

    if [ -n "$UNDOCUMENTED_DIRS" ]; then
      WARNINGS="${WARNINGS}[Context Drift] High-churn directories with no documentation:\n${UNDOCUMENTED_DIRS}"
      SHOULD_WARN=true
    fi
  fi
fi

# --- Output ---

if [ "$SHOULD_WARN" = true ]; then
  # Record warning timestamp (cooldown)
  date +%s > "$STATE_FILE"

  printf "%b" "$WARNINGS"
  printf "\nTo silence for %d days: warnings will auto-suppress until next cycle.\n" "$COOLDOWN_DAYS"
  printf "To update docs now: consider running /review or updating CLAUDE.md with recent changes.\n"
fi

exit 0
