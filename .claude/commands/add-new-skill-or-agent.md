---
name: add-new-skill-or-agent
description: Workflow command scaffold for add-new-skill-or-agent in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-skill-or-agent

Use this workflow when working on **add-new-skill-or-agent** in `everything-claude-code`.

## Goal

Adds a new skill or agent to the system, including documentation and configuration.

## Common Files

- `.agents/skills/*/SKILL.md`
- `.agents/skills/*/agents/openai.yaml`
- `skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`
- `AGENTS.md`
- `rules/common/agents.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update SKILL.md in .agents/skills/{skill-name}/
- Add or update agents/openai.yaml in .agents/skills/{skill-name}/agents/
- Optionally, add SKILL.md in skills/{skill-name}/ and/or .cursor/skills/{skill-name}/
- Register agent in AGENTS.md if applicable
- Update rules/common/agents.md if applicable

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.