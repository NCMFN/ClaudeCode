#!/bin/bash
# Mindset Primer — UserPromptSubmit hook
# Reinforces critical meta-cognitive instructions near every prompt.
# Rotates phrasing to prevent habituation (same message = fades to noise).
# Cost: ~15-20 tokens per prompt.

PRIMERS=(
  "Confidence is not evidence — verify. Maximum cognitive effort. No lazy assumptions."
  "Verify, don't assume. Deep effort. Challenge your first instinct."
  "The more certain you feel, the more you must check. No shortcuts."
  "Evidence over intuition. Full effort. Question what seems obvious."
  "Stop and verify before claiming done. Think harder, not faster."
  "Say 'I don't know' rather than guessing. Read the code — don't infer from the name."
  "Re-read what you just wrote as a skeptic would. What looks wrong?"
  "What did you miss? Assume you missed something. Find it."
)

# Rotate based on a simple counter (prompt count this session)
COUNTER_FILE="/tmp/claude-mindset-counter-${SESSION_ID:-$$}"
COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
INDEX=$((COUNT % ${#PRIMERS[@]}))
echo "$((COUNT + 1))" > "$COUNTER_FILE" 2>/dev/null

echo "${PRIMERS[$INDEX]}"
