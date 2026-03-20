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
feat: implement --with/--without selective install flags
```

*Commit message example*

```text
chore: prepare v1.9.0 release (#666)
```

*Commit message example*

```text
fix: resolve Windows CI failures and markdown lint (#667)
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
feat(skills): add architecture-decision-records skill (#555)
```

*Commit message example*

```text
feat(commands): add /context-budget optimizer command (#554)
```

*Commit message example*

```text
feat(skills): add codebase-onboarding skill (#553)
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
- `schemas/*`
- `**/*.test.*`
- `**/api/**`

**Example commit sequence**:
```
feat: record canonical session snapshots via adapters (#511)
fix: resolve all CI test failures (19 fixes across 6 files) (#519)
feat(skills): add documentation-lookup, bun-runtime, nextjs-turbopack; feat(agents): add rust-reviewer
```

### Add New Skill

Adds a new skill to the codebase, following documentation and review conventions.

**Frequency**: ~6 times per month

**Steps**:
1. Create skills/<skill-name>/SKILL.md with full documentation (When to Use, How It Works, Examples, etc).
2. Optionally add cross-harness copies in .agents/skills/<skill-name>/SKILL.md and/or .cursor/skills/<skill-name>/SKILL.md.
3. Address PR review feedback by updating SKILL.md (sections, examples, headings, etc).
4. Sync or remove duplicate copies to match canonical version in skills/.
5. If skill integrates with Antigravity or Codex, add openai.yaml or agents/ subdir as needed.

**Files typically involved**:
- `skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`

**Example commit sequence**:
```
Create skills/<skill-name>/SKILL.md with full documentation (When to Use, How It Works, Examples, etc).
Optionally add cross-harness copies in .agents/skills/<skill-name>/SKILL.md and/or .cursor/skills/<skill-name>/SKILL.md.
Address PR review feedback by updating SKILL.md (sections, examples, headings, etc).
Sync or remove duplicate copies to match canonical version in skills/.
If skill integrates with Antigravity or Codex, add openai.yaml or agents/ subdir as needed.
```

### Add New Agent

Registers a new agent, including documentation and catalog updates.

**Frequency**: ~3 times per month

**Steps**:
1. Create agents/<agent-name>.md with agent details.
2. Register the agent in AGENTS.md (table and/or summary).
3. Update README.md with agent count and/or agent tree.
4. If agent is related to a language, update rules/common/agents.md or similar.
5. If agent is for a new language, add to install manifests as needed.

**Files typically involved**:
- `agents/*.md`
- `AGENTS.md`
- `README.md`
- `rules/common/agents.md`

**Example commit sequence**:
```
Create agents/<agent-name>.md with agent details.
Register the agent in AGENTS.md (table and/or summary).
Update README.md with agent count and/or agent tree.
If agent is related to a language, update rules/common/agents.md or similar.
If agent is for a new language, add to install manifests as needed.
```

### Add New Command

Adds a new slash command to the system, with documentation.

**Frequency**: ~2 times per month

**Steps**:
1. Create commands/<command-name>.md with frontmatter and usage guide.
2. If command is agent-backed, add or update agents/<agent-name>.md.
3. If command is skill-backed, add or update skills/<skill-name>/SKILL.md.
4. Update documentation or mapping files (e.g. docs/COMMAND-AGENT-MAP.md) as needed.

**Files typically involved**:
- `commands/*.md`
- `agents/*.md`
- `skills/*/SKILL.md`
- `docs/COMMAND-AGENT-MAP.md`

**Example commit sequence**:
```
Create commands/<command-name>.md with frontmatter and usage guide.
If command is agent-backed, add or update agents/<agent-name>.md.
If command is skill-backed, add or update skills/<skill-name>/SKILL.md.
Update documentation or mapping files (e.g. docs/COMMAND-AGENT-MAP.md) as needed.
```

### Add New Language Support

Adds support for a new programming language, including agents, rules, commands, and tests.

**Frequency**: ~1 times per month

**Steps**:
1. Create agents/<language>-reviewer.md and agents/<language>-build-resolver.md.
2. Create rules/<language>/* (coding-style.md, hooks.md, patterns.md, security.md, testing.md).
3. Create skills/<language>-patterns/SKILL.md and skills/<language>-testing/SKILL.md.
4. Create commands/<language>-build.md, commands/<language>-review.md, commands/<language>-test.md.
5. Register agents in AGENTS.md and update documentation counts.
6. Add or update install manifests for new skills/agents.
7. Add or update tests for language hooks and commands.

**Files typically involved**:
- `agents/*-reviewer.md`
- `agents/*-build-resolver.md`
- `rules/*/*.md`
- `skills/*-patterns/SKILL.md`
- `skills/*-testing/SKILL.md`
- `commands/*-build.md`
- `commands/*-review.md`
- `commands/*-test.md`
- `AGENTS.md`
- `README.md`
- `manifests/install-*.json`
- `tests/hooks/*.test.js`

**Example commit sequence**:
```
Create agents/<language>-reviewer.md and agents/<language>-build-resolver.md.
Create rules/<language>/* (coding-style.md, hooks.md, patterns.md, security.md, testing.md).
Create skills/<language>-patterns/SKILL.md and skills/<language>-testing/SKILL.md.
Create commands/<language>-build.md, commands/<language>-review.md, commands/<language>-test.md.
Register agents in AGENTS.md and update documentation counts.
Add or update install manifests for new skills/agents.
Add or update tests for language hooks and commands.
```

### Update Install Manifests And Schema

Updates install component/module/profile manifests and schemas to add new skills/agents or install features.

**Frequency**: ~2 times per month

**Steps**:
1. Edit manifests/install-components.json, install-modules.json, and/or install-profiles.json to add new entries.
2. Update schemas/install-components.schema.json if the manifest structure changes (e.g. new family prefixes).
3. Update scripts/lib/install-manifests.js for new logic or validation.
4. Add or update tests for install logic and selective install features.

**Files typically involved**:
- `manifests/install-components.json`
- `manifests/install-modules.json`
- `manifests/install-profiles.json`
- `schemas/install-components.schema.json`
- `scripts/lib/install-manifests.js`
- `tests/lib/selective-install.test.js`

**Example commit sequence**:
```
Edit manifests/install-components.json, install-modules.json, and/or install-profiles.json to add new entries.
Update schemas/install-components.schema.json if the manifest structure changes (e.g. new family prefixes).
Update scripts/lib/install-manifests.js for new logic or validation.
Add or update tests for install logic and selective install features.
```

### Catalog Count And Documentation Sync

Synchronizes agent/skill/command counts and documentation tables across AGENTS.md, README.md, and related files.

**Frequency**: ~3 times per month

**Steps**:
1. Update agent/skill/command counts in AGENTS.md and README.md (quick-start, tables, summaries).
2. Update agent/skill tables in AGENTS.md.
3. Update docs/COMMAND-AGENT-MAP.md if new commands/agents were added.
4. Optionally update package.json or CI scripts to enforce catalog integrity.
5. Optionally update zh-CN/README.md or other localized docs.

**Files typically involved**:
- `AGENTS.md`
- `README.md`
- `docs/COMMAND-AGENT-MAP.md`
- `docs/zh-CN/README.md`
- `package.json`
- `scripts/ci/catalog.js`

**Example commit sequence**:
```
Update agent/skill/command counts in AGENTS.md and README.md (quick-start, tables, summaries).
Update agent/skill tables in AGENTS.md.
Update docs/COMMAND-AGENT-MAP.md if new commands/agents were added.
Optionally update package.json or CI scripts to enforce catalog integrity.
Optionally update zh-CN/README.md or other localized docs.
```

### Address Pr Review Feedback

Iteratively updates files to address code review feedback, especially for new skills, agents, or commands.

**Frequency**: ~6 times per month

**Steps**:
1. Edit SKILL.md, agent, or command files to fix section headings, examples, or workflow descriptions.
2. Sync or remove duplicate files (e.g. .agents/skills/*/SKILL.md) as requested.
3. Clarify or correct workflow steps and examples.
4. Update related documentation or mapping files as needed.

**Files typically involved**:
- `skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.cursor/skills/*/SKILL.md`
- `agents/*.md`
- `commands/*.md`
- `docs/COMMAND-AGENT-MAP.md`

**Example commit sequence**:
```
Edit SKILL.md, agent, or command files to fix section headings, examples, or workflow descriptions.
Sync or remove duplicate files (e.g. .agents/skills/*/SKILL.md) as requested.
Clarify or correct workflow steps and examples.
Update related documentation or mapping files as needed.
```

### Add Or Update Observer Or Hook Script

Adds or updates observer logic or shell hook scripts, often with corresponding tests.

**Frequency**: ~2 times per month

**Steps**:
1. Edit skills/continuous-learning-v2/hooks/*.sh or agents/observer-loop.sh scripts.
2. Add or update logic for process management, throttling, or sandboxing.
3. Update or add corresponding tests in tests/hooks/*.test.js.
4. Address PR review feedback by refining logic or adding guards.

**Files typically involved**:
- `skills/continuous-learning-v2/hooks/*.sh`
- `skills/continuous-learning-v2/agents/observer-loop.sh`
- `tests/hooks/*.test.js`

**Example commit sequence**:
```
Edit skills/continuous-learning-v2/hooks/*.sh or agents/observer-loop.sh scripts.
Add or update logic for process management, throttling, or sandboxing.
Update or add corresponding tests in tests/hooks/*.test.js.
Address PR review feedback by refining logic or adding guards.
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
