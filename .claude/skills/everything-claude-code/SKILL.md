---
name: everything-claude-code-conventions
description: Development conventions and patterns for everything-claude-code. JavaScript project with conventional commits.
---

# Everything Claude Code Conventions

> Generated from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) on 2026-03-20

## Overview

This skill teaches Claude the development patterns and conventions used in everything-claude-code.

## Tech Stack

- **Primary Language**: JavaScript
- **Architecture**: hybrid module organization
- **Test Location**: separate

## When to Use This Skill

Activate this skill when:
- Making changes to this repository
- Adding new features following established patterns
- Writing tests that match project conventions
- Creating commits with proper message format

## Commit Conventions

Follow these commit message conventions based on 500 analyzed commits.

### Commit Style: Conventional Commits

### Prefixes Used

- `fix`
- `test`
- `feat`
- `docs`

### Message Guidelines

- Average message length: ~65 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
fix: address PR review feedback for C# skills
```

*Commit message example*

```text
feat: add csharp-data-access skill for EF Core and Dapper patterns
```

*Commit message example*

```text
chore: prepare v1.9.0 release (#666)
```

*Commit message example*

```text
docs: add Antigravity setup and usage guide (#552)
```

*Commit message example*

```text
merge: PR #529 — feat(skills): add documentation-lookup, bun-runtime, nextjs-turbopack; feat(agents): add rust-reviewer
```

*Commit message example*

```text
feat: add C# / .NET 8+ language support (rules, skills, docs)
```

*Commit message example*

```text
fix: resolve Windows CI failures and markdown lint (#667)
```

*Commit message example*

```text
feat(skills): add architecture-decision-records skill (#555)
```

## Architecture

### Project Structure: Single Package

This project uses **hybrid** module organization.

### Configuration Files

- `.github/workflows/ci.yml`
- `.github/workflows/maintenance.yml`
- `.github/workflows/monthly-metrics.yml`
- `.github/workflows/release.yml`
- `.github/workflows/reusable-release.yml`
- `.github/workflows/reusable-test.yml`
- `.github/workflows/reusable-validate.yml`
- `.opencode/package.json`
- `.opencode/tsconfig.json`
- `.prettierrc`
- `eslint.config.js`
- `package.json`

### Guidelines

- This project uses a hybrid organization
- Follow existing patterns when adding new code

## Code Style

### Language: JavaScript

### Naming Conventions

| Element | Convention |
|---------|------------|
| Files | camelCase |
| Functions | camelCase |
| Classes | PascalCase |
| Constants | SCREAMING_SNAKE_CASE |

### Import Style: Mixed Style

### Export Style: Mixed Style


## Testing

### Test Framework

No specific test framework detected — use the repository's existing test patterns.

### File Pattern: `*.test.js`

### Test Types

- **Unit tests**: Test individual functions and components in isolation
- **Integration tests**: Test interactions between multiple components/services

### Coverage

This project has coverage reporting configured. Aim for 80%+ coverage.


## Error Handling

### Error Handling Style: Try-Catch Blocks


*Standard error handling pattern*

```typescript
try {
  const result = await riskyOperation()
  return result
} catch (error) {
  console.error('Operation failed:', error)
  throw new Error('User-friendly message')
}
```

## Common Workflows

These workflows were detected from analyzing commit patterns.

### Feature Development

Standard feature implementation workflow

**Frequency**: ~22 times per month

**Steps**:
1. Add feature implementation
2. Add tests for feature
3. Update documentation

**Files typically involved**:
- `manifests/*`
- `**/*.test.*`
- `**/api/**`

**Example commit sequence**:
```
feat(skills): add documentation-lookup, bun-runtime, nextjs-turbopack; feat(agents): add rust-reviewer
docs(skills): align documentation-lookup with CONTRIBUTING template; add cross-harness (Codex/Cursor) skill copies
fix: address PR review — skill template (When to use, How it works, Examples), bun.lock, next build note, rust-reviewer CI note, doc-lookup privacy/uncertainty
```

### Add New Skill

Adds a new skill to the repository, following the SKILL.md format and conventions.

**Frequency**: ~5 times per month

**Steps**:
1. Create a new directory under skills/ (e.g., skills/skill-name/).
2. Add SKILL.md with required sections (When to Use, How It Works, Examples, etc.).
3. Optionally add cross-harness copies in .agents/skills/ and .cursor/skills/ if needed.
4. Address PR review feedback to align with CONTRIBUTING.md conventions.
5. Sync or remove cross-harness copies as needed after review.

**Files typically involved**:
- `skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`

**Example commit sequence**:
```
Create a new directory under skills/ (e.g., skills/skill-name/).
Add SKILL.md with required sections (When to Use, How It Works, Examples, etc.).
Optionally add cross-harness copies in .agents/skills/ and .cursor/skills/ if needed.
Address PR review feedback to align with CONTRIBUTING.md conventions.
Sync or remove cross-harness copies as needed after review.
```

### Add New Agent

Adds a new agent to the repository, including registration and documentation updates.

**Frequency**: ~3 times per month

**Steps**:
1. Create a new agent markdown file under agents/ (e.g., agents/agent-name.md).
2. Register the agent in AGENTS.md (add to summary table and/or project structure).
3. Update README.md with agent count and/or agent tree if needed.
4. Optionally update rules/common/agents.md or docs/COMMAND-AGENT-MAP.md if mapping is needed.
5. Address PR review feedback for format and registration.

**Files typically involved**:
- `agents/*.md`
- `AGENTS.md`
- `README.md`
- `rules/common/agents.md`
- `docs/COMMAND-AGENT-MAP.md`

**Example commit sequence**:
```
Create a new agent markdown file under agents/ (e.g., agents/agent-name.md).
Register the agent in AGENTS.md (add to summary table and/or project structure).
Update README.md with agent count and/or agent tree if needed.
Optionally update rules/common/agents.md or docs/COMMAND-AGENT-MAP.md if mapping is needed.
Address PR review feedback for format and registration.
```

### Add Language Support

Adds support for a new programming language, including rules, agents, and commands.

**Frequency**: ~2 times per month

**Steps**:
1. Create rules for the language under rules/<language>/ (coding-style.md, hooks.md, patterns.md, security.md, testing.md).
2. Add relevant agents (e.g., reviewer, build-resolver) under agents/ and register in AGENTS.md.
3. Add skills for language-specific patterns and testing under skills/.
4. Add commands for build/review/test under commands/.
5. Update README.md, AGENTS.md, and other documentation with new language and agent/skill counts.
6. Add or update tests for new language features if needed.

**Files typically involved**:
- `rules/*/*.md`
- `agents/*.md`
- `skills/*/SKILL.md`
- `commands/*.md`
- `AGENTS.md`
- `README.md`
- `tests/**/*`

**Example commit sequence**:
```
Create rules for the language under rules/<language>/ (coding-style.md, hooks.md, patterns.md, security.md, testing.md).
Add relevant agents (e.g., reviewer, build-resolver) under agents/ and register in AGENTS.md.
Add skills for language-specific patterns and testing under skills/.
Add commands for build/review/test under commands/.
Update README.md, AGENTS.md, and other documentation with new language and agent/skill counts.
Add or update tests for new language features if needed.
```

### Register Agent Or Skill In Catalog

Updates catalog files and documentation to reflect new or changed agents/skills.

**Frequency**: ~5 times per month

**Steps**:
1. Update AGENTS.md summary table and/or project structure.
2. Update README.md quick-start, agent/skill/command counts, and agent tree.
3. Update docs/COMMAND-AGENT-MAP.md or rules/common/agents.md if mapping is needed.
4. Update package.json or other catalog integrity files if required.
5. Sync documentation counts with actual catalog state.

**Files typically involved**:
- `AGENTS.md`
- `README.md`
- `docs/COMMAND-AGENT-MAP.md`
- `rules/common/agents.md`
- `package.json`

**Example commit sequence**:
```
Update AGENTS.md summary table and/or project structure.
Update README.md quick-start, agent/skill/command counts, and agent tree.
Update docs/COMMAND-AGENT-MAP.md or rules/common/agents.md if mapping is needed.
Update package.json or other catalog integrity files if required.
Sync documentation counts with actual catalog state.
```

### Add New Command

Adds a new slash command to the repository, including documentation and mapping.

**Frequency**: ~2 times per month

**Steps**:
1. Create a new command markdown file under commands/ (e.g., commands/command-name.md).
2. If the command is agent-backed, ensure the agent exists and is registered.
3. Update docs/COMMAND-AGENT-MAP.md if mapping is required.
4. Update README.md or AGENTS.md if command count or mapping is referenced.
5. Address PR review feedback for format and completeness.

**Files typically involved**:
- `commands/*.md`
- `docs/COMMAND-AGENT-MAP.md`
- `README.md`
- `AGENTS.md`

**Example commit sequence**:
```
Create a new command markdown file under commands/ (e.g., commands/command-name.md).
If the command is agent-backed, ensure the agent exists and is registered.
Update docs/COMMAND-AGENT-MAP.md if mapping is required.
Update README.md or AGENTS.md if command count or mapping is referenced.
Address PR review feedback for format and completeness.
```

### Cross Harness Skill Sync

Ensures skills are available across different harnesses (Codex, Cursor) by syncing or removing duplicate SKILL.md files.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update SKILL.md in skills/ directory.
2. Copy or sync SKILL.md to .agents/skills/ and/or .cursor/skills/ as needed.
3. Address PR review feedback to ensure canonical version is in skills/, and duplicates are removed if not needed.
4. Document or clarify harness-specific behaviors in the skill file if required.

**Files typically involved**:
- `skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`

**Example commit sequence**:
```
Add or update SKILL.md in skills/ directory.
Copy or sync SKILL.md to .agents/skills/ and/or .cursor/skills/ as needed.
Address PR review feedback to ensure canonical version is in skills/, and duplicates are removed if not needed.
Document or clarify harness-specific behaviors in the skill file if required.
```

### Address Pr Review Feedback

Iteratively refines code, documentation, or skills in response to PR review comments.

**Frequency**: ~10 times per month

**Steps**:
1. Edit relevant files (skills, agents, scripts, docs) to address review comments.
2. Rename sections, clarify examples, fix code or documentation issues as requested.
3. Sync or update cross-harness copies if needed.
4. Repeat until all review comments are resolved.

**Files typically involved**:
- `skills/*/SKILL.md`
- `agents/*.md`
- `README.md`
- `AGENTS.md`
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`
- `tests/**/*`
- `scripts/**/*`

**Example commit sequence**:
```
Edit relevant files (skills, agents, scripts, docs) to address review comments.
Rename sections, clarify examples, fix code or documentation issues as requested.
Sync or update cross-harness copies if needed.
Repeat until all review comments are resolved.
```

### Update Install Manifests

Keeps install profiles, modules, and components up to date with new or missing skills.

**Frequency**: ~1 times per month

**Steps**:
1. Edit manifests/install-components.json, install-modules.json, and install-profiles.json to add or remove skills.
2. Ensure all skills are referenced in at least one module/profile.
3. Validate manifest integrity (e.g., via validate-install-manifests script).

**Files typically involved**:
- `manifests/install-components.json`
- `manifests/install-modules.json`
- `manifests/install-profiles.json`

**Example commit sequence**:
```
Edit manifests/install-components.json, install-modules.json, and install-profiles.json to add or remove skills.
Ensure all skills are referenced in at least one module/profile.
Validate manifest integrity (e.g., via validate-install-manifests script).
```


## Best Practices

Based on analysis of the codebase, follow these practices:

### Do

- Use conventional commit format (feat:, fix:, etc.)
- Follow *.test.js naming pattern
- Use camelCase for file names
- Prefer mixed exports

### Don't

- Don't write vague commit messages
- Don't skip tests for new features
- Don't deviate from established patterns without discussion

---

*This skill was auto-generated by [ECC Tools](https://ecc.tools). Review and customize as needed for your team.*
