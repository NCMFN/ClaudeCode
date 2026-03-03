#!/bin/bash
# Session Analyzer - Async Stop Hook
# Reads session tracker data, detects patterns, writes findings to learned/.
# Closes the feedback loop: tool observations -> pattern detection -> instinct creation.
#
# Hook: Stop, matcher: *
# Performance: <100ms (reads pre-computed JSON, no LLM call)
# Safety: Fast execution + cleanup trap. Failures don't block session end.

set -e

TRACKER_DIR="/tmp/claude-session-tracker"
# Prevent symlink attack
if [ -L "$TRACKER_DIR" ]; then
  exit 0
fi
LEARNED_DIR="${HOME}/.claude/learned"
TODAY=$(date +%Y-%m-%d)
LEARNED_FILE="${LEARNED_DIR}/${TODAY}-auto.md"

mkdir -p "$LEARNED_DIR"

# Read hook input from stdin
INPUT=$(head -c 102400)
if [ -z "$INPUT" ]; then
  exit 0
fi

# Extract session ID (Stop hooks may not have session_id — fallback to transcript path)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // ""' 2>/dev/null)
if [ "$SESSION_ID" = "null" ] || [ -z "$SESSION_ID" ]; then
  # Fallback: extract UUID from transcript_path filename
  TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path // ""' 2>/dev/null)
  if [ -n "$TRANSCRIPT_PATH" ] && [ "$TRANSCRIPT_PATH" != "null" ]; then
    SESSION_ID=$(basename "$TRANSCRIPT_PATH" .jsonl)
  fi
fi

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
  # Last resort: find the most recently modified tracker file
  LATEST_TRACKER=$(ls -t "${TRACKER_DIR}"/*.json 2>/dev/null | head -1)
  if [ -n "$LATEST_TRACKER" ]; then
    SESSION_ID=$(basename "$LATEST_TRACKER" .json)
  else
    exit 0
  fi
fi

TRACKER_FILE="${TRACKER_DIR}/${SESSION_ID}.json"
if [ ! -f "$TRACKER_FILE" ]; then
  exit 0
fi

# Acquire session lock before reading (prevents race with PostToolUse writing)
LOCK_FILE="${TRACKER_DIR}/${SESSION_ID}.lock"
if ! shlock -f "$LOCK_FILE" -p $$ 2>/dev/null; then
  # Lock contention — skip rather than block session end
  exit 0
fi

# Ensure lock + tracker are cleaned up even on early exit
cleanup() { rm -f "$TRACKER_FILE" "$LOCK_FILE"; }
trap cleanup EXIT

TRACKER=$(cat "$TRACKER_FILE")
FINDINGS=""

# --- Error Pattern Detection ---
# Check each error category for 3+ occurrences
ERROR_CATEGORIES=$(echo "$TRACKER" | jq -r '.errors | to_entries[] | select(.value >= 3) | "\(.key):\(.value)"' 2>/dev/null)

while IFS=: read -r category count; do
  [ -z "$category" ] && continue

  # Build description based on category
  case "$category" in
    bash_error)
      pattern_desc="Repeated bash command failures. Check command syntax, paths, and prerequisites before execution."
      ;;
    failed_edit)
      pattern_desc="Repeated Edit tool failures (string not found/not unique). Read the file first; use more surrounding context for unique matching."
      ;;
    type_error)
      pattern_desc="Repeated TypeScript type errors. Run tsc --noEmit to verify types before making further changes."
      ;;
    *)
      pattern_desc="Repeated errors of type '${category}'."
      ;;
  esac

  FINDINGS="${FINDINGS}
## Auto-detected: Repeated ${category} errors

Session: ${SESSION_ID}, Date: ${TODAY}
Occurred ${count} times.
Pattern: ${pattern_desc}

"
done <<< "$ERROR_CATEGORIES"

# --- Retry Sequence Detection ---
RETRY_COUNT=$(echo "$TRACKER" | jq '.retry_sequences | length' 2>/dev/null)
if [ "${RETRY_COUNT:-0}" -gt 0 ]; then
  RETRIES=$(echo "$TRACKER" | jq -r '.retry_sequences[] | "- \(.tool) on \(.target | .[0:100]): \(.count) consecutive failures"' 2>/dev/null)
  FINDINGS="${FINDINGS}
## Auto-detected: Retry sequences (3+ consecutive failures on same target)

Session: ${SESSION_ID}, Date: ${TODAY}
${RETRIES}

Consider: Step back and rethink the approach when hitting 3+ failures. Read the file again, check assumptions, or try a different strategy.

"
fi

# --- Parallelization Audit ---
# Analyze files_modified: group by directory prefix
AGENT_CALLS=$(echo "$TRACKER" | jq '.agent_calls // 0' 2>/dev/null)
FILE_COUNT=$(echo "$TRACKER" | jq '.files_modified | length' 2>/dev/null)

if [ "${FILE_COUNT:-0}" -ge 4 ] && [ "${AGENT_CALLS:-0}" -eq 0 ]; then
  # Extract directory prefixes and count unique clusters
  CLUSTERS=$(echo "$TRACKER" | jq -r '
    .files_modified[]
  ' 2>/dev/null | while read -r filepath; do
    # Extract first two path segments after common prefixes
    echo "$filepath" | sed -E 's|^.*/src/|src/|; s|^.*/app/|app/|; s|^.*/pages/|pages/|; s|^.*/lib/|lib/|; s|^.*/tests?/|tests/|' | cut -d'/' -f1-2
  done | sort -u)

  CLUSTER_COUNT=$(echo "$CLUSTERS" | grep -c . 2>/dev/null || echo 0)

  if [ "$CLUSTER_COUNT" -ge 3 ]; then
    CLUSTER_LIST=$(echo "$CLUSTERS" | sed 's/^/  - /')
    FINDINGS="${FINDINGS}
## Auto-detected: Missed parallelization opportunity

Session: ${SESSION_ID}, Date: ${TODAY}
${FILE_COUNT} files modified across ${CLUSTER_COUNT}+ independent clusters, with 0 agent delegations.
Clusters:
${CLUSTER_LIST}

Consider: Use parallel agents with file ownership per cluster when modifying 3+ independent directories.

"
  fi
fi

# --- Tool Distribution Anomalies ---
TOTAL_TOOLS=$(echo "$TRACKER" | jq '[.tools[]] | add // 0' 2>/dev/null)
if [ "${TOTAL_TOOLS:-0}" -ge 20 ]; then
  # Check for unusually high Bash ratio (>60%) which suggests underuse of dedicated tools
  BASH_COUNT=$(echo "$TRACKER" | jq '.tools.Bash // 0' 2>/dev/null)
  if [ "$BASH_COUNT" -gt 0 ]; then
    BASH_PCT=$((BASH_COUNT * 100 / TOTAL_TOOLS))
    if [ "$BASH_PCT" -gt 60 ]; then
      FINDINGS="${FINDINGS}
## Auto-detected: High Bash usage ratio (${BASH_PCT}%)

Session: ${SESSION_ID}, Date: ${TODAY}
Bash was ${BASH_PCT}% of ${TOTAL_TOOLS} tool calls.
Consider: Use dedicated tools (Read, Grep, Glob, Edit) instead of bash equivalents (cat, grep, find, sed).

"
    fi
  fi
fi

# --- Write findings ---
if [ -n "$FINDINGS" ]; then
  # Write to temp file first, then atomic append (prevents torn writes from concurrent sessions)
  TEMP_FINDINGS=$(mktemp "${LEARNED_DIR}/.findings.XXXXXX")
  {
    echo "# Auto-detected patterns - ${TODAY}"
    echo "$FINDINGS"
  } > "$TEMP_FINDINGS"
  cat "$TEMP_FINDINGS" >> "$LEARNED_FILE"
  rm -f "$TEMP_FINDINGS"
fi

# Cleanup handled by EXIT trap
exit 0
