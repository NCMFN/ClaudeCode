#!/bin/bash
# Layer 0: Skill Auto-Indexer
# Hook: SessionStart
# Scans all SKILL.md files, extracts YAML frontmatter, generates skill-index.json
# This eliminates manual maintenance — new skills are indexed automatically.
#
# Output: ~/.claude/hooks/skill-router/skill-index.json
# Cost: Runs once per session (~50ms for 50 skills)

SKILLS_DIR="${HOME}/.claude/skills"
INDEX_FILE="${HOME}/.claude/hooks/skill-router/skill-index.json"

# Find all SKILL.md files, following symlinks
skill_files=$(find -L "$SKILLS_DIR" -name "SKILL.md" -type f 2>/dev/null)

if [ -z "$skill_files" ]; then
  echo '{"skills":[],"generated_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}' > "$INDEX_FILE"
  echo "[SkillIndexer] No skills found" >&2
  exit 0
fi

# Parse YAML frontmatter from each SKILL.md and build JSON index
# Uses pure bash + jq — no Python dependency for startup speed
entries="[]"

while IFS= read -r file; do
  # Extract YAML frontmatter (between --- delimiters)
  in_frontmatter=false
  frontmatter=""
  while IFS= read -r line; do
    if [ "$line" = "---" ]; then
      if [ "$in_frontmatter" = true ]; then
        break
      else
        in_frontmatter=true
        continue
      fi
    fi
    if [ "$in_frontmatter" = true ]; then
      frontmatter="${frontmatter}${line}"$'\n'
    fi
  done < "$file"

  # Extract fields from YAML (simple key: value parsing, no nested YAML)
  name=$(echo "$frontmatter" | grep -E '^name:' | head -1 | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
  description=$(echo "$frontmatter" | grep -E '^description:' | head -1 | sed 's/^description:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
  use_when=$(echo "$frontmatter" | grep -E '^use-when:' | head -1 | sed 's/^use-when:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
  user_invocable=$(echo "$frontmatter" | grep -E '^user-invocable:' | head -1 | sed 's/^user-invocable:[[:space:]]*//')

  # Skip if no name or description
  if [ -z "$name" ] && [ -z "$description" ]; then
    continue
  fi

  # Derive the skill directory name (used as skill identifier)
  skill_dir=$(basename "$(dirname "$file")")

  # If name is empty, use directory name
  if [ -z "$name" ]; then
    name="$skill_dir"
  fi

  # Build search text: combine description + use_when for matching
  search_text="${description} ${use_when}"
  # Lowercase for case-insensitive matching later
  search_lower=$(echo "$search_text" | tr '[:upper:]' '[:lower:]')

  # Determine if this is a background skill (user-invocable: false)
  is_background="false"
  if [ "$user_invocable" = "false" ]; then
    is_background="true"
  fi

  # Add entry to JSON array
  entry=$(jq -n \
    --arg name "$name" \
    --arg dir "$skill_dir" \
    --arg description "$description" \
    --arg use_when "$use_when" \
    --arg search "$search_lower" \
    --arg path "$file" \
    --argjson background "$is_background" \
    '{name: $name, dir: $dir, description: $description, use_when: $use_when, search: $search, path: $path, background: $background}')

  entries=$(echo "$entries" | jq --argjson entry "$entry" '. + [$entry]')
done <<< "$skill_files"

# Write the index
skill_count=$(echo "$entries" | jq 'length')
jq -n \
  --argjson skills "$entries" \
  --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson count "$skill_count" \
  '{skills: $skills, generated_at: $generated_at, count: $count}' > "$INDEX_FILE"

# --- Also index instincts for the surfacer ---
INSTINCT_INDEX_FILE="${HOME}/.claude/hooks/skill-router/instinct-index.json"
INSTINCT_DIR="${HOME}/.claude/homunculus/instincts/personal"

if [ -d "$INSTINCT_DIR" ]; then
  instinct_entries="[]"
  instinct_files=$(find -L "$INSTINCT_DIR" -name "*.md" -type f 2>/dev/null)

  while IFS= read -r ifile; do
    [ -z "$ifile" ] && continue

    # Extract YAML frontmatter
    in_fm=false
    fm=""
    while IFS= read -r iline; do
      if [ "$iline" = "---" ]; then
        if [ "$in_fm" = true ]; then break; else in_fm=true; continue; fi
      fi
      if [ "$in_fm" = true ]; then fm="${fm}${iline}"$'\n'; fi
    done < "$ifile"

    i_trigger=$(echo "$fm" | grep -E '^trigger:' | head -1 | sed 's/^trigger:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
    i_domain=$(echo "$fm" | grep -E '^domain:' | head -1 | sed 's/^domain:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
    i_confidence=$(echo "$fm" | grep -E '^confidence:' | head -1 | sed 's/^confidence:[[:space:]]*//')
    i_phase=$(echo "$fm" | grep -E '^phase:' | head -1 | sed 's/^phase:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')

    # Extract first content line after ## Action heading from markdown body
    i_action=$(awk '/^## Action/{found=1; next} found && /^[^#]/ && NF{print; exit}' "$ifile")

    [ -z "$i_trigger" ] && continue

    # Build triggers array from trigger text (split on commas or spaces)
    triggers_lower=$(echo "$i_trigger" | tr '[:upper:]' '[:lower:]' | tr -cs '[:alnum:]' '\n' | awk 'length >= 3' | sort -u)
    triggers_json=$(echo "$triggers_lower" | jq -R -s 'split("\n") | map(select(length > 0))')

    # Summary is first 120 chars of the action body
    summary=$(echo "$i_action" | head -c 120)

    i_entry=$(jq -n \
      --arg id "$(basename "$ifile" .md)" \
      --argjson triggers "$triggers_json" \
      --arg domain "${i_domain:-general}" \
      --arg phase "${i_phase:-general}" \
      --arg summary "$summary" \
      --argjson confidence "${i_confidence:-0.50}" \
      '{id: $id, triggers: $triggers, domain: $domain, phase: $phase, summary: $summary, confidence: $confidence}')

    instinct_entries=$(echo "$instinct_entries" | jq --argjson e "$i_entry" '. + [$e]')
  done <<< "$instinct_files"

  instinct_count=$(echo "$instinct_entries" | jq 'length')
  jq -n \
    --argjson instincts "$instinct_entries" \
    --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson count "$instinct_count" \
    '{instincts: $instincts, generated_at: $generated_at, count: $count}' > "$INSTINCT_INDEX_FILE"

  echo "[SkillIndexer] Indexed $instinct_count instincts → $INSTINCT_INDEX_FILE" >&2
else
  echo '{"instincts":[],"generated_at":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","count":0}' > "$INSTINCT_INDEX_FILE"
fi

echo "[SkillIndexer] Indexed $skill_count skills → $INDEX_FILE" >&2
