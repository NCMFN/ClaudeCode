---
name: add-or-update-command-doc
description: Workflow command scaffold for add-or-update-command-doc in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-update-command-doc

Use this workflow when working on **add-or-update-command-doc** in `everything-claude-code`.

## Goal

Adds or updates a command documentation file in the ECC bundle.

## Common Files

- `.claude/commands/add-or-update-skill.md`
- `.claude/commands/feature-development.md`
- `.claude/commands/database-migration.md`
- `.claude/commands/add-or-update-skill-documentation.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update .claude/commands/{command-name}.md

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.