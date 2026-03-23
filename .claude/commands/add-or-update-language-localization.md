---
name: add-or-update-language-localization
description: Workflow command scaffold for add-or-update-language-localization in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-or-update-language-localization

Use this workflow when working on **add-or-update-language-localization** in `everything-claude-code`.

## Goal

Adds or updates documentation and guides for a new or existing language localization (e.g., Chinese, Turkish, Brazilian Portuguese).

## Common Files

- `README.md`
- `docs/zh-CN/**`
- `docs/tr/**`
- `docs/pt-BR/**`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Add or update multiple files under docs/<lang>/ (agents, commands, skills, rules, guides, etc.)
- Update README.md to reflect new language and increment language count
- Optionally update or add language-specific images or references

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.