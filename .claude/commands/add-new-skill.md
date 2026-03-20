---
name: add-new-skill
description: Workflow command scaffold for add-new-skill in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-skill

Use this workflow when working on **add-new-skill** in `everything-claude-code`.

## Goal

Adds a new skill to the system, including documentation and sometimes scripts.

## Common Files

- `skills/*/SKILL.md`
- `skills/*/scripts/*.sh`
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

- Create a new directory under skills/ with the skill name.
- Add SKILL.md with full documentation of the skill.
- Optionally add scripts/ subdirectory with supporting scripts.
- Optionally add .agents/skills/ and/or .cursor/skills/ copies for cross-harness support.
- Update AGENTS.md and/or README.md skill counts if necessary.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.