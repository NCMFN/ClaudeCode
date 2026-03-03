#!/bin/bash
# Layer 2: Prompt-Time Skill Router
# Hook: UserPromptSubmit
# Reads user prompt, matches against skill-index.json, injects recommendations
# into Claude's context via stdout.
#
# Matching strategy:
#   1. Extract significant words from user prompt (3+ chars, lowercased)
#   2. For each skill, count how many prompt words appear in its search text
#   3. Rank by match count, recommend top 1-3 with 2+ word matches
#
# Cost: ~30ms (pure bash + jq, no LLM call)
# Output: stdout text → injected into Claude's context as system reminder

INDEX_FILE="${HOME}/.claude/hooks/skill-router/skill-index.json"
INSTINCT_INDEX_FILE="${HOME}/.claude/hooks/skill-router/instinct-index.json"
LOG_FILE="${HOME}/.claude/hooks/skill-router/recommendations.jsonl"

# Read stdin (hook receives JSON with session context)
input=$(cat)

# Extract the user's prompt text
# UserPromptSubmit stdin includes the prompt in tool_input or as the message
prompt=$(echo "$input" | jq -r '.tool_input.prompt // .tool_input.message // .user_prompt // ""' 2>/dev/null)

# If we couldn't extract a prompt, try the raw content
if [ -z "$prompt" ] || [ "$prompt" = "null" ]; then
  prompt=$(echo "$input" | jq -r '.content // ""' 2>/dev/null)
fi

# If still empty, exit silently (don't block)
if [ -z "$prompt" ] || [ "$prompt" = "null" ]; then
  exit 0
fi

# Check if index exists
if [ ! -f "$INDEX_FILE" ]; then
  # Try to regenerate index on the fly
  "${HOME}/.claude/hooks/skill-router/index-skills.sh" < /dev/null 2>/dev/null
  if [ ! -f "$INDEX_FILE" ]; then
    exit 0
  fi
fi

# Lowercase the prompt for matching
prompt_lower=$(echo "$prompt" | tr '[:upper:]' '[:lower:]')

# Extract significant words (3+ chars, alphanumeric only, deduplicated)
# Filter out common stopwords
# Stopwords: ONLY grammatical words. Domain terms (build, code, test, page, etc.)
# are kept because they are critical matching signals for skill routing.
prompt_words=$(echo "$prompt_lower" | tr -cs '[:alnum:]' '\n' | awk 'length >= 3' | sort -u | grep -vxE '(the|and|for|are|but|not|you|all|can|had|her|was|one|our|out|has|his|how|its|may|new|now|old|see|way|who|did|get|let|say|she|too|use|with|this|that|from|have|been|will|more|when|what|some|them|than|also|just|like|into|over|such|take|very|most|only|come|made|after|being|here|much|many|does|your|each|about|would|could|should|before|between|those|these|other|which|their|there|where|still|every|while|might|through|going|right)')

# Extract all skill data in ONE jq call (not N calls per skill)
# Format: TAB-separated lines: name\tdir\tdescription\tsearch\tbackground
skill_data=$(jq -r '.skills[] | [.name, .dir, .description, .search, (.background | tostring)] | @tsv' "$INDEX_FILE")

results=""
while IFS=$'\t' read -r skill_name skill_dir skill_desc search_text is_bg; do
  [ -z "$skill_name" ] && continue

  # Skip background skills (user-invocable: false)
  [ "$is_bg" = "true" ] && continue

  # Count how many prompt words appear in the skill's search text
  match_count=0
  matched_words=""
  while IFS= read -r word; do
    [ -z "$word" ] && continue
    # Use word-boundary prefix match (\bword) so "page" matches "pages",
    # "fix" matches "fixing", "review" matches "reviewing", etc.
    if echo "$search_text" | grep -qi "\b${word}"; then
      match_count=$((match_count + 1))
      matched_words="${matched_words} ${word}"
    fi
  done <<< "$prompt_words"

  # Only consider skills with 2+ word matches
  if [ "$match_count" -ge 2 ]; then
    results="${results}${match_count}|${skill_name}|${skill_dir}|${skill_desc}|${matched_words}"$'\n'
  fi
done <<< "$skill_data"

# Sort by match count (descending), take top 3
if [ -n "$results" ]; then
  top_matches=$(echo "$results" | sort -t'|' -k1 -nr | head -3)

  # Build the recommendation output
  recommendation="[Skill Router] Relevant skills detected for this task:"
  while IFS='|' read -r count name dir desc words; do
    [ -z "$count" ] && continue
    recommendation="${recommendation}
- **${name}** (${count} keyword matches:${words}) — ${desc}"
  done <<< "$top_matches"

  recommendation="${recommendation}
Consider loading these skills with the Skill tool if not already loaded."

  # Log recommendation for analysis
  prompt_trunc=$(echo "$prompt" | head -c 200)
  skills_json=$(echo "$top_matches" | while IFS='|' read -r c n d desc w; do
    [ -z "$c" ] && continue
    printf '{"skill":"%s","matches":%s,"words":"%s"},' "$n" "$c" "$(echo "$w" | sed 's/^ //')"
  done | sed 's/,$//')
  printf '{"ts":"%s","prompt":"%s","recommended":[%s]}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$(echo "$prompt_trunc" | jq -Rs '.' | sed 's/^"//;s/"$//')" \
    "$skills_json" >> "$LOG_FILE" 2>/dev/null

  # Output to stdout — this gets injected into Claude's context
  echo "$recommendation"
else
  # Log no-match events too (for false-negative analysis)
  prompt_trunc=$(echo "$prompt" | head -c 200)
  printf '{"ts":"%s","prompt":"%s","recommended":[]}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$(echo "$prompt_trunc" | jq -Rs '.' | sed 's/^"//;s/"$//')" >> "$LOG_FILE" 2>/dev/null
fi

# --- Instinct Surfacing ---
# Detect session phase from tracker data and surface relevant instincts
PHASE="general"
SESSION_ID=$(echo "$input" | jq -r '.session_id // ""' 2>/dev/null)
if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
  # Fallback: find most recent tracker file
  LATEST_TRACKER=$(ls -t /tmp/claude-session-tracker/*.json 2>/dev/null | head -1)
  if [ -n "$LATEST_TRACKER" ]; then
    SESSION_ID=$(basename "$LATEST_TRACKER" .json)
  fi
fi

TRACKER_FILE="/tmp/claude-session-tracker/${SESSION_ID}.json"
if [ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ] && [ -f "$TRACKER_FILE" ]; then
  # Phase detection from tool usage ratios
  total=$(jq '[.tools[]] | add // 1' "$TRACKER_FILE" 2>/dev/null)
  if [ "${total:-0}" -gt 5 ]; then
    read_count=$(jq '.tools.Read // 0' "$TRACKER_FILE" 2>/dev/null)
    edit_count=$(jq '.tools.Edit // 0' "$TRACKER_FILE" 2>/dev/null)
    bash_count=$(jq '.tools.Bash // 0' "$TRACKER_FILE" 2>/dev/null)
    websearch_count=$(jq '.tools.WebSearch // 0' "$TRACKER_FILE" 2>/dev/null)

    read_pct=$((read_count * 100 / total))
    edit_pct=$((edit_count * 100 / total))
    bash_pct=$((bash_count * 100 / total))
    ws_pct=$((websearch_count * 100 / total))

    if [ "$ws_pct" -gt 30 ]; then PHASE="research"
    elif [ "$read_pct" -gt 50 ]; then PHASE="investigation"
    elif [ "$edit_pct" -gt 35 ]; then PHASE="editing"
    elif [ "$bash_pct" -gt 45 ]; then PHASE="execution"
    fi
  fi
fi

# Surface instincts if index exists
if [ -f "$INSTINCT_INDEX_FILE" ]; then
  # Single jq call: filter by phase, match prompt keywords, rank by score
  instinct_output=$(jq -r --arg phase "$PHASE" --arg words "$prompt_lower" '
    [.instincts[] |
      select(.phase == $phase or .phase == "general" or .phase == null) |
      . + {match_count: (
        [.triggers[] | select($words | contains(.))] | length
      )}
    ] |
    sort_by(-.confidence, -.match_count) |
    [.[] | select(.match_count > 0)] |
    .[0:3] |
    if length > 0 then
      "[Instinct Surfacer] Phase: \($phase)\n" +
      ([.[] | "- \(.summary) (confidence: \(.confidence))"] | join("\n"))
    else empty end
  ' "$INSTINCT_INDEX_FILE" 2>/dev/null)

  if [ -n "$instinct_output" ]; then
    echo "$instinct_output"
  fi
fi

exit 0
