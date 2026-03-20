---
name: add-new-skill
description: Workflow command scaffold for add-new-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-skill

Use this workflow when working on **add-new-skill** in `everything-claude-code`.

## Goal

Adds a new skill to the everything-claude-code project, including documentation and configuration.

## Common Files

- `.claude/commands/add-new-skill.md`
- `.agents/skills/everything-claude-code/SKILL.md`
- `.claude/skills/everything-claude-code/SKILL.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update '.claude/commands/add-new-skill.md' with instructions or documentation for the new skill.
- Create or update '.agents/skills/everything-claude-code/SKILL.md' to document the skill's details.
- Create or update '.claude/skills/everything-claude-code/SKILL.md' for additional documentation or configuration.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.