---
name: add-documentation-command-or-skill-or-agent-or-workflow
description: Workflow command scaffold for add-documentation-command-or-skill-or-agent-or-workflow in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-documentation-command-or-skill-or-agent-or-workflow

Use this workflow when working on **add-documentation-command-or-skill-or-agent-or-workflow** in `everything-claude-code`.

## Goal

Adds new documentation for a command, skill, agent, or workflow to the ECC bundle.

## Common Files

- `.claude/commands/add-documentation-command-or-skill-or-agent-or-workflow.md`
- `.claude/commands/add-documentation-command-or-skill.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new markdown file in .claude/commands/ with a descriptive name (e.g., add-documentation-command-or-skill-or-agent-or-workflow.md or add-documentation-command-or-skill.md).
- Commit the new file with a message referencing the ECC bundle.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.