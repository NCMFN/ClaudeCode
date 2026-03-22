---
name: add-or-update-skill-documentation
description: Workflow command scaffold for add-or-update-skill-documentation in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-update-skill-documentation

Use this workflow when working on **add-or-update-skill-documentation** in `everything-claude-code`.

## Goal

Adds a new skill or updates documentation for an existing skill, typically by creating or modifying a SKILL.md file under skills/ or docs/[lang]/skills/.

## Common Files

- `skills/*/SKILL.md`
- `docs/*/skills/*/SKILL.md`
- `AGENTS.md`
- `README.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update SKILL.md in the appropriate skills/ or docs/[lang]/skills/ directory
- Optionally update AGENTS.md or README.md to reflect new skill count or catalog
- Optionally add or update related diagrams or documentation files

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.