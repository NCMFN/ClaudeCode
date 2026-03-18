---
name: feature-development-documentation
description: Workflow command scaffold for feature-development-documentation in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /feature-development-documentation

Use this workflow when working on **feature-development-documentation** in `everything-claude-code`.

## Goal

Documents the process or workflow for developing a new feature in the system.

## Common Files

- `.claude/commands/feature-development.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update '.claude/commands/feature-development.md'.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.