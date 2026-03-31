---
name: add-new-agent-or-skill
description: Workflow command scaffold for add-new-agent-or-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-agent-or-skill

Use this workflow when working on **add-new-agent-or-skill** in `everything-claude-code`.

## Goal

Adds a new agent or skill to the system, including agent definition, skill documentation, and optionally references or helper scripts.

## Common Files

- `agents/*.md`
- `skills/*/SKILL.md`
- `skills/*/references/*`
- `skills/*/agents/*`
- `AGENTS.md`
- `manifests/install-modules.json`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create agent definition in agents/ or skills/<skill>/SKILL.md
- Add supporting files (e.g., references, scripts, rules) under skills/<skill>/
- Update AGENTS.md and/or manifests/install-modules.json if needed
- Add or update related tests if applicable

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.