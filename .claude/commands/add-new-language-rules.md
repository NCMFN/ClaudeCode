---
name: add-new-language-rules
description: Workflow command scaffold for add-new-language-rules in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-language-rules

Use this workflow when working on **add-new-language-rules** in `everything-claude-code`.

## Goal

Adds support for a new programming language by introducing language-specific rule files for coding style, hooks, patterns, security, and testing.

## Common Files

- `rules/<language>/coding-style.md`
- `rules/<language>/hooks.md`
- `rules/<language>/patterns.md`
- `rules/<language>/security.md`
- `rules/<language>/testing.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new directory under rules/<language>/
- Add coding-style.md, hooks.md, patterns.md, security.md, and testing.md files with language-specific content
- Optionally update documentation or catalog counts if needed

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.