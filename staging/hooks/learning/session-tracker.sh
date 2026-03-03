#!/bin/bash
# Session Tracker - Async PostToolUse Hook
# Maintains per-session counters for tools, errors, files, and retry sequences.
# Data feeds the session analyzer (Stop hook) and instinct surfacer (UserPromptSubmit).
#
# Hook: PostToolUse, matcher: *
# Performance: <50ms per call (JSON increment via jq + flock, no LLM)
# Safety: Fast execution + set -e + exit 0 on lock contention. Failures don't block Claude.

set -e

TRACKER_DIR="/tmp/claude-session-tracker"
# Prevent symlink attack: if path exists as a symlink, refuse to use it
if [ -L "$TRACKER_DIR" ]; then
  exit 0
fi
mkdir -p -m 700 "$TRACKER_DIR"

# Read hook input from stdin
INPUT=$(head -c 102400)
if [ -z "$INPUT" ]; then
  exit 0
fi

# Extract fields from hook JSON
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // .tool // "unknown"' 2>/dev/null)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null)
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // .input // ""' 2>/dev/null)
TOOL_OUTPUT=$(echo "$INPUT" | jq -r '.tool_output // .output // ""' 2>/dev/null)

# Bail if we can't identify the session
if [ "$SESSION_ID" = "unknown" ] || [ "$SESSION_ID" = "null" ] || [ -z "$SESSION_ID" ]; then
  exit 0
fi

TRACKER_FILE="${TRACKER_DIR}/${SESSION_ID}.json"
LOCK_FILE="${TRACKER_DIR}/${SESSION_ID}.lock"

# Acquire per-session lock to prevent concurrent writes (macOS uses shlock)
if ! shlock -f "$LOCK_FILE" -p $$ 2>/dev/null; then
  exit 0
fi
# Ensure lock is released on exit
trap 'rm -f "$LOCK_FILE"' EXIT

# Initialize tracker file if it doesn't exist
if [ ! -f "$TRACKER_FILE" ]; then
  cat > "$TRACKER_FILE" << 'INIT'
{
  "tools": {},
  "errors": {},
  "files_modified": [],
  "agent_calls": 0,
  "retry_sequences": [],
  "_last_tool": null,
  "_last_target": null,
  "_consecutive_fails": 0
}
INIT
fi

# --- Increment tool count ---
TRACKER=$(cat "$TRACKER_FILE")
TRACKER=$(echo "$TRACKER" | jq --arg tool "$TOOL_NAME" '
  .tools[$tool] = ((.tools[$tool] // 0) + 1)
')

# --- Track agent calls ---
if [ "$TOOL_NAME" = "Agent" ] || [ "$TOOL_NAME" = "Task" ]; then
  TRACKER=$(echo "$TRACKER" | jq '.agent_calls += 1')
fi

# --- Detect errors ---
ERROR_TYPE=""

# Bash: check for unambiguous failure indicators in output
# NOTE: bare "error" excluded — matches false positives ("0 errors found", "error handling")
if [ "$TOOL_NAME" = "Bash" ]; then
  if echo "$TOOL_OUTPUT" | grep -qiE '(command not found|permission denied|No such file or directory|ENOENT|EACCES|exit code [1-9]|exited with code [1-9]|non-zero exit|returned non-zero|fatal:|panic:|segmentation fault|killed|cannot find module)' 2>/dev/null; then
    ERROR_TYPE="bash_error"
  fi
fi

# Edit: check for failed edit indicators
if [ "$TOOL_NAME" = "Edit" ]; then
  if echo "$TOOL_OUTPUT" | grep -qiE '(not found in|not unique|could not find|no match)' 2>/dev/null; then
    ERROR_TYPE="failed_edit"
  fi
fi

# TypeScript errors in Bash output
if [ "$TOOL_NAME" = "Bash" ]; then
  if echo "$TOOL_OUTPUT" | grep -qE 'error TS[0-9]' 2>/dev/null; then
    ERROR_TYPE="type_error"
  fi
fi

# Record error if detected
if [ -n "$ERROR_TYPE" ]; then
  TRACKER=$(echo "$TRACKER" | jq --arg etype "$ERROR_TYPE" '
    .errors[$etype] = ((.errors[$etype] // 0) + 1)
  ')
fi

# --- Track files modified ---
if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
  FILE_PATH=""
  if echo "$TOOL_INPUT" | jq -e '.file_path' >/dev/null 2>&1; then
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // ""' 2>/dev/null)
  elif echo "$TOOL_INPUT" | jq -e '.' >/dev/null 2>&1; then
    : # tool_input is JSON but no file_path
  else
    # tool_input might be a raw string containing a path
    FILE_PATH=$(echo "$TOOL_INPUT" | grep -oE '/[^ "]+\.[a-zA-Z]+' | head -1 2>/dev/null || true)
  fi

  if [ -n "$FILE_PATH" ] && [ "$FILE_PATH" != "null" ]; then
    TRACKER=$(echo "$TRACKER" | jq --arg fp "$FILE_PATH" '
      if (.files_modified | index($fp)) then . else .files_modified += [$fp] end
    ')
  fi
fi

# --- Retry sequence detection ---
# Track consecutive failed attempts at same tool + same target
TARGET=""
if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
  TARGET=$(echo "$TOOL_INPUT" | jq -r '.file_path // ""' 2>/dev/null)
elif [ "$TOOL_NAME" = "Bash" ]; then
  TARGET=$(echo "$TOOL_INPUT" | jq -r '.command // ""' 2>/dev/null | head -c 100)
fi

LAST_TOOL=$(echo "$TRACKER" | jq -r '._last_tool // ""')
LAST_TARGET=$(echo "$TRACKER" | jq -r '._last_target // ""')
CONSECUTIVE=$(echo "$TRACKER" | jq -r '._consecutive_fails // 0')

if [ -n "$ERROR_TYPE" ] && [ "$TOOL_NAME" = "$LAST_TOOL" ] && [ "$TARGET" = "$LAST_TARGET" ] && [ -n "$TARGET" ]; then
  CONSECUTIVE=$((CONSECUTIVE + 1))
  TRACKER=$(echo "$TRACKER" | jq --argjson c "$CONSECUTIVE" '._consecutive_fails = $c')

  # If 3+ consecutive failures on same tool+target, record the retry sequence
  if [ "$CONSECUTIVE" -ge 3 ]; then
    TRACKER=$(echo "$TRACKER" | jq --arg tool "$TOOL_NAME" --arg target "$TARGET" --argjson count "$CONSECUTIVE" '
      .retry_sequences += [{"tool": $tool, "target": ($target | .[0:200]), "count": $count, "all_failed": true}]
    ')
  fi
elif [ -n "$ERROR_TYPE" ]; then
  # New failed tool/target combo - reset counter
  TRACKER=$(echo "$TRACKER" | jq '._consecutive_fails = 1')
else
  # Success - reset counter
  TRACKER=$(echo "$TRACKER" | jq '._consecutive_fails = 0')
fi

# Update last tool/target tracking
TRACKER=$(echo "$TRACKER" | jq --arg tool "$TOOL_NAME" --arg target "${TARGET:-}" '
  ._last_tool = $tool | ._last_target = $target
')

# Write back atomically
TEMP_FILE=$(mktemp "${TRACKER_DIR}/.tmp.XXXXXX")
echo "$TRACKER" > "$TEMP_FILE"
mv "$TEMP_FILE" "$TRACKER_FILE"

exit 0
