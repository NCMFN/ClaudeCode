---
name: add-new-agent
description: Workflow command scaffold for add-new-agent in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-agent

Use this workflow when working on **add-new-agent** in `everything-claude-code`.

## Goal

Adds a new agent to the everything-claude-code project, including documentation and configuration.

## Common Files

- `.claude/commands/add-new-agent.md`
- `.agents/skills/everything-claude-code/agents/openai.yaml`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create or update '.claude/commands/add-new-agent.md' with instructions or documentation for the new agent.
- Create or update '.agents/skills/everything-claude-code/agents/openai.yaml' for agent configuration.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.