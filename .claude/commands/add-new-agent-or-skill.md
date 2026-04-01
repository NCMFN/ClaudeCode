---
name: add-new-agent-or-skill
description: Workflow command scaffold for add-new-agent-or-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-agent-or-skill

Use this workflow when working on **add-new-agent-or-skill** in `everything-claude-code`.

## Goal

Adds a new agent or skill to the codebase, including documentation and/or configuration.

## Common Files

- `skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.claude/skills/*/SKILL.md`
- `agents/*.md`
- `.codex/agents/*.toml`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update SKILL.md in skills/ or .agents/skills/ or .claude/skills/
- Optionally add agent definition in agents/ directory
- Optionally add configuration in .codex/agents/ or similar
- Update relevant manifest or index files if needed

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.