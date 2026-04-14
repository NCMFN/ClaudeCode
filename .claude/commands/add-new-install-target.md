---
name: add-new-install-target
description: Workflow command scaffold for add-new-install-target in everything-claude-code.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /add-new-install-target

Use this workflow when working on **add-new-install-target** in `everything-claude-code`.

## Goal

Adds support for a new install target (e.g., Gemini, CodeBuddy) so ECC can be installed on a new platform or IDE.

## Common Files

- `manifests/install-modules.json`
- `schemas/ecc-install-config.schema.json`
- `schemas/install-modules.schema.json`
- `scripts/lib/install-manifests.js`
- `scripts/lib/install-targets/{target}-project.js`
- `scripts/lib/install-targets/registry.js`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Create a new install target script (e.g., scripts/lib/install-targets/{target}-project.js, .{target}/install.sh, .{target}/install.js)
- Add documentation for the new target (e.g., .{target}/README.md, .{target}/README.zh-CN.md, .{target}/GEMINI.md)
- Update manifests/install-modules.json to register the new target
- Update schemas/ecc-install-config.schema.json and schemas/install-modules.schema.json for schema validation
- Update scripts/lib/install-manifests.js and scripts/lib/install-targets/registry.js to handle the new target

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.