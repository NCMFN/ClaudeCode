---
name: add-new-skill
description: Workflow command scaffold for add-new-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-skill

Use this workflow when working on **add-new-skill** in `everything-claude-code`.

## Goal

Adds a new skill to the system, including documentation and implementation files.

## Common Files

- `skills/*/SKILL.md`
- `skills/*/scripts/*.py`
- `skills/*/prompts/*.md`
- `skills/*/fixtures/*`
- `skills/*/tests/*.py`
- `AGENTS.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new directory under skills/ with the skill name.
- Add SKILL.md documentation file describing the skill.
- Add supporting files (e.g., scripts, prompts, fixtures, tests) as needed.
- Update AGENTS.md and/or README.md to reflect new skill count or catalog.
- Commit all new files together.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.