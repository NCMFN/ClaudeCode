---
name: add-new-skill
description: Workflow command scaffold for add-new-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-skill

Use this workflow when working on **add-new-skill** in `everything-claude-code`.

## Goal

Adds a new skill to the system, often with supporting scripts and documentation. Frequently includes review/feedback fixes.

## Common Files

- `skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`
- `AGENTS.md`
- `README.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create SKILL.md in skills/<skill-name>/SKILL.md
- Optionally add scripts or supporting files in skills/<skill-name>/scripts/
- If Antigravity/Codex/Cursor support: add .agents/skills/<skill-name>/SKILL.md and/or .cursor/skills/<skill-name>/SKILL.md
- Update AGENTS.md and README.md skill/command counts if needed
- Address PR review feedback with follow-up commits

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.