---
name: update-team-or-identity-config
description: Workflow command scaffold for update-team-or-identity-config in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /update-team-or-identity-config

Use this workflow when working on **update-team-or-identity-config** in `everything-claude-code`.

## Goal

Updates team configuration or identity files, likely to reflect changes in team structure or system identity.

## Common Files

- `.claude/team/everything-claude-code-team-config.json`
- `.claude/identity.json`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Edit .claude/team/everything-claude-code-team-config.json or .claude/identity.json.
- Commit the changes.
- Optionally, inform team members or trigger downstream automation.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.