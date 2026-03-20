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

- `feat`
- `fix`
- `test`
- `docs`

### Message Guidelines

- Average message length: ~66 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/add-command-or-skill-bundle.md)
```

*Commit message example*

```text
chore(deps-dev): bump flatted (#675)
```

*Commit message example*

```text
fix: auto-detect ECC root from plugin cache when CLAUDE_PLUGIN_ROOT is unset (#547) (#691)
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
feat: add everything-claude-code ECC bundle (.claude/commands/feature-development.md)
```

*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/database-migration.md)
```

*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/enterprise/controls.md)
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

### Import Style: Relative Imports

### Export Style: Mixed Style


*Preferred import style*

```typescript
// Use relative imports
import { Button } from '../components/Button'
import { useAuth } from './hooks/useAuth'
```

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

**Frequency**: ~30 times per month

**Steps**:
1. Add feature implementation
2. Add tests for feature
3. Update documentation

**Example commit sequence**:
```
feat: add everything-claude-code ECC bundle (.claude/team/everything-claude-code-team-config.json)
feat: add everything-claude-code ECC bundle (.claude/enterprise/controls.md)
feat: add everything-claude-code ECC bundle (.claude/commands/database-migration.md)
```

### Add Command Or Skill Bundle

Adds a new command or skill bundle to the ECC system, typically as a markdown documentation or configuration file.

**Frequency**: ~4 times per month

**Steps**:
1. Create a new markdown file in .claude/commands/ or .claude/skills/ or .agents/skills/ directory.
2. Document the new command or skill in the respective SKILL.md or command file.
3. Optionally, update related configuration files.

**Files typically involved**:
- `.claude/commands/*.md`
- `.claude/skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`

**Example commit sequence**:
```
Create a new markdown file in .claude/commands/ or .claude/skills/ or .agents/skills/ directory.
Document the new command or skill in the respective SKILL.md or command file.
Optionally, update related configuration files.
```

### Update Team Or Identity Config

Updates team configuration or identity files, likely to reflect changes in team structure or system identity.

**Frequency**: ~3 times per month

**Steps**:
1. Edit .claude/team/everything-claude-code-team-config.json or .claude/identity.json.
2. Commit the changes.
3. Optionally, inform team members or trigger downstream automation.

**Files typically involved**:
- `.claude/team/everything-claude-code-team-config.json`
- `.claude/identity.json`

**Example commit sequence**:
```
Edit .claude/team/everything-claude-code-team-config.json or .claude/identity.json.
Commit the changes.
Optionally, inform team members or trigger downstream automation.
```

### Add Or Update Research Or Rules Playbook

Adds or updates research playbooks or rules/guardrails documentation to guide development and maintain standards.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update a markdown file in .claude/research/ or .claude/rules/.
2. Document the new or revised process or rule.
3. Commit the changes.

**Files typically involved**:
- `.claude/research/*.md`
- `.claude/rules/*.md`

**Example commit sequence**:
```
Create or update a markdown file in .claude/research/ or .claude/rules/.
Document the new or revised process or rule.
Commit the changes.
```

### Add Or Update Ecc Tools Config

Adds or updates the ECC tools configuration to register new tools or update tool metadata.

**Frequency**: ~2 times per month

**Steps**:
1. Edit .claude/ecc-tools.json.
2. Commit the changes.

**Files typically involved**:
- `.claude/ecc-tools.json`

**Example commit sequence**:
```
Edit .claude/ecc-tools.json.
Commit the changes.
```

### Add Or Update Codex Agent Config

Adds or updates agent configuration files for the Codex system, enabling new agent roles or capabilities.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update a .toml file in .codex/agents/.
2. Commit the changes.

**Files typically involved**:
- `.codex/agents/*.toml`

**Example commit sequence**:
```
Create or update a .toml file in .codex/agents/.
Commit the changes.
```

### Add Or Update Enterprise Controls

Adds or updates enterprise controls documentation or configuration.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update .claude/enterprise/controls.md.
2. Commit the changes.

**Files typically involved**:
- `.claude/enterprise/controls.md`

**Example commit sequence**:
```
Create or update .claude/enterprise/controls.md.
Commit the changes.
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
