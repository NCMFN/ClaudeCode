---
name: add-new-skill
description: Workflow command scaffold for add-new-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-skill

Use this workflow when working on **add-new-skill** in `everything-claude-code`.

## Goal

Adds a new skill to the project, including documentation, fixtures, prompts, scripts, and tests.

## Common Files

- `skills/*/SKILL.md`
- `skills/*/fixtures/*`
- `skills/*/prompts/*`
- `skills/*/scripts/*`
- `skills/*/tests/*`
- `AGENTS.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new directory under skills/ with the skill name
- Add SKILL.md documentation file
- Add supporting files: fixtures, prompts, scripts, tests as needed
- Update AGENTS.md and/or README.md to reflect the new skill count or catalog
- Commit all new files

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.