#!/bin/bash
# Health Check - SessionStart Hook
# Silent on success. Only outputs warnings for broken components.
# Budget: <50ms. Unix philosophy: no news is good news.
#
# Hook: SessionStart, matcher: *, async: false (fast enough to run sync)

WARNINGS=""
STATUS_FILE="${HOME}/.claude/hooks/.health-status"

warn() {
  WARNINGS="${WARNINGS}[HealthCheck] WARN: $1\n"
}

# --- Check 1: Required binaries (~3ms) ---
for bin in jq shlock shasum awk git; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    warn "$bin not found in PATH"
  fi
done

# --- Check 2: Critical hook scripts exist and are executable (~2ms) ---
HOOK_SCRIPTS=(
  "${HOME}/.claude/hooks/skill-router/route-skills.sh"
  "${HOME}/.claude/hooks/skill-router/index-skills.sh"
  "${HOME}/.claude/hooks/learning/session-tracker.sh"
  "${HOME}/.claude/hooks/learning/session-analyze.sh"
)
for script in "${HOOK_SCRIPTS[@]}"; do
  if [ ! -f "$script" ]; then
    warn "$(basename "$script") missing"
  elif [ ! -x "$script" ]; then
    warn "$(basename "$script") not executable"
  fi
done

# --- Check 3: /tmp/claude-session-tracker/ is writable (~1ms) ---
TRACKER_DIR="/tmp/claude-session-tracker"
if [ -L "$TRACKER_DIR" ]; then
  warn "session-tracker dir is a symlink (security risk)"
elif [ -d "$TRACKER_DIR" ] && [ ! -w "$TRACKER_DIR" ]; then
  warn "session-tracker dir not writable"
fi

# --- Check 4: Index files exist, valid JSON, not stale (~10ms) ---
for idx_file in \
  "${HOME}/.claude/hooks/skill-router/skill-index.json" \
  "${HOME}/.claude/hooks/skill-router/instinct-index.json"; do
  name=$(basename "$idx_file")
  if [ ! -f "$idx_file" ]; then
    warn "$name missing"
  elif ! jq -e '.count' "$idx_file" >/dev/null 2>&1; then
    warn "$name is corrupt (invalid JSON)"
  else
    # Check staleness: modified within 7 days
    if [ "$(uname)" = "Darwin" ]; then
      mtime=$(stat -f %m "$idx_file" 2>/dev/null)
    else
      mtime=$(stat -c %Y "$idx_file" 2>/dev/null)
    fi
    now=$(date +%s)
    age_days=$(( (now - ${mtime:-0}) / 86400 ))
    if [ "$age_days" -gt 7 ]; then
      warn "$name is ${age_days} days old (stale)"
    fi
  fi
done

# --- Check 5: LaunchAgents loaded (skip if checked within 24h) ---
AGENT_CHECK_FILE="${HOME}/.claude/hooks/.agent-check-ts"
now=$(date +%s)
last_check=0
if [ -f "$AGENT_CHECK_FILE" ]; then
  last_check=$(cat "$AGENT_CHECK_FILE" 2>/dev/null)
fi

if [ $((now - last_check)) -gt 86400 ]; then
  for agent in com.claude.observer com.claude.consolidation; do
    if ! launchctl list "$agent" >/dev/null 2>&1; then
      warn "LaunchAgent $agent not loaded"
    fi
  done
  echo "$now" > "$AGENT_CHECK_FILE"
fi

# --- Check 6: Reinforcement directory exists ---
if [ ! -d "${HOME}/.claude/homunculus/reinforcement" ]; then
  mkdir -p "${HOME}/.claude/homunculus/reinforcement" 2>/dev/null
fi

# --- Output ---
if [ -n "$WARNINGS" ]; then
  printf '%b' "$WARNINGS"
  printf 'WARN %s %b' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$WARNINGS" > "$STATUS_FILE"
else
  echo "OK $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATUS_FILE"
fi
