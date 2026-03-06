#!/bin/bash
PROPOSALS_DIR="$HOME/.claude/intel-proposals/pending"
[ -d "$PROPOSALS_DIR" ] || exit 0

FILES=()
while IFS= read -r -d '' f; do
  FILES+=("$f")
done < <(find "$PROPOSALS_DIR" -maxdepth 1 -name "*.json" -print0 2>/dev/null)

COUNT=${#FILES[@]}
[ "$COUNT" -eq 0 ] && exit 0

echo "[Intel] $COUNT pending proposal(s) from bookmarked articles:"
for f in "${FILES[@]}"; do
  SUMMARY=$(jq -r '.metadata.sourceTitle // "Untitled"' "$f" 2>/dev/null)
  TYPE=$(jq -r '.proposals[0].type // "unknown"' "$f" 2>/dev/null)
  echo "  - $SUMMARY ($TYPE)"
done
echo "[Intel] Say 'review proposals' or run /review-proposals to review and apply."
