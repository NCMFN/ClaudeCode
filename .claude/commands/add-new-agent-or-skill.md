---
name: add-new-agent-or-skill
description: Workflow command scaffold for add-new-agent-or-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-agent-or-skill

Use this workflow when working on **add-new-agent-or-skill** in `everything-claude-code`.

## Goal

Adds a new agent or skill to the codebase, including documentation and configuration.

## Common Files

- `agents/*.md`
- `skills/*/SKILL.md`
- `AGENTS.md`
- `README.md`
- `.opencode/opencode.json`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new agent or skill definition file (e.g., agents/<name>.md or skills/<name>/SKILL.md).
- Update or add related documentation (e.g., README.md, AGENTS.md).
- Register the agent or skill in configuration files if necessary (e.g., .opencode/opencode.json).

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.