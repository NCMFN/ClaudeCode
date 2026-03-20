---
name: add-command-or-skill-bundle
description: Workflow command scaffold for add-command-or-skill-bundle in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-command-or-skill-bundle

Use this workflow when working on **add-command-or-skill-bundle** in `everything-claude-code`.

## Goal

Adds a new command or skill bundle to the ECC system, typically as a markdown documentation or configuration file.

## Common Files

- `.claude/commands/*.md`
- `.claude/skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new markdown file in .claude/commands/ or .claude/skills/ or .agents/skills/ directory.
- Document the new command or skill in the respective SKILL.md or command file.
- Optionally, update related configuration files.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.