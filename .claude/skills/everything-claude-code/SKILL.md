---
name: everything-claude-code-conventions
description: Development conventions and patterns for everything-claude-code. JavaScript project with conventional commits.
---

# Everything Claude Code Conventions

> Generated from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) on 2026-04-01

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
- `feat`
- `docs`
- `chore`

### Message Guidelines

- Average message length: ~57 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/add-new-command-or-workflow.md)
```

*Commit message example*

```text
fix: update ecc2 ratatui dependency
```

*Commit message example*

```text
docs: tighten pr backlog classification
```

*Commit message example*

```text
refactor: fold social graph ranking into lead intelligence
```

*Commit message example*

```text
chore: ignore local orchestration artifacts
```

*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/add-new-agent-or-skill.md)
```

*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/feature-development.md)
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

**Frequency**: ~20 times per month

**Steps**:
1. Add feature implementation
2. Add tests for feature
3. Update documentation

**Files typically involved**:
- `.opencode/*`
- `.opencode/plugins/*`
- `.opencode/plugins/lib/*`
- `**/*.test.*`

**Example commit sequence**:
```
feat(team-builder): use `claude agents` command for agent discovery (#1021)
fix: extract inline SessionStart bootstrap to separate file (#1035)
feat: add hexagonal architecture SKILL. (#1034)
```

### Add New Agent Or Skill

Adds a new agent or skill to the codebase, including documentation and/or configuration.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update SKILL.md in skills/ or .agents/skills/ or .claude/skills/
2. Optionally add agent definition in agents/ directory
3. Optionally add configuration in .codex/agents/ or similar
4. Update relevant manifest or index files if needed

**Files typically involved**:
- `skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `.claude/skills/*/SKILL.md`
- `agents/*.md`
- `.codex/agents/*.toml`

**Example commit sequence**:
```
Create or update SKILL.md in skills/ or .agents/skills/ or .claude/skills/
Optionally add agent definition in agents/ directory
Optionally add configuration in .codex/agents/ or similar
Update relevant manifest or index files if needed
```

### Add Or Update Command Workflow

Adds or updates a command or workflow, typically as a markdown file describing a process or automation.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update a markdown file in commands/ or .claude/commands/
2. Document the workflow, usage, and steps
3. Optionally update index or manifest files

**Files typically involved**:
- `commands/*.md`
- `.claude/commands/*.md`

**Example commit sequence**:
```
Create or update a markdown file in commands/ or .claude/commands/
Document the workflow, usage, and steps
Optionally update index or manifest files
```

### Feature Or Skill Development With Review Fixes

Implements a new feature, agent, or skill, then iteratively addresses review feedback with follow-up fixes.

**Frequency**: ~2 times per month

**Steps**:
1. Initial implementation: add new files for feature/skill/agent
2. Submit for review
3. Apply fixes in follow-up commits addressing review findings (e.g., documentation, code changes, config updates)
4. Repeat as needed until approval

**Files typically involved**:
- `skills/*/SKILL.md`
- `agents/*.md`
- `commands/*.md`
- `manifests/*.json`
- `schemas/*.json`
- `scripts/**/*.js`

**Example commit sequence**:
```
Initial implementation: add new files for feature/skill/agent
Submit for review
Apply fixes in follow-up commits addressing review findings (e.g., documentation, code changes, config updates)
Repeat as needed until approval
```

### Dependency Bump Github Actions

Automated or manual update of GitHub Actions workflow dependencies to new versions.

**Frequency**: ~3 times per month

**Steps**:
1. Update version numbers in one or more .github/workflows/*.yml files
2. Commit with a message referencing the dependency and new version
3. Optionally update related documentation or lockfiles

**Files typically involved**:
- `.github/workflows/*.yml`

**Example commit sequence**:
```
Update version numbers in one or more .github/workflows/*.yml files
Commit with a message referencing the dependency and new version
Optionally update related documentation or lockfiles
```

### Install Target Addition Or Update

Adds or updates an install target (e.g., new IDE integration) with scripts, manifests, and schema updates.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update install scripts (install.js, install.sh, uninstall.js, uninstall.sh) in a target directory
2. Update manifests/install-modules.json
3. Update schemas/ecc-install-config.schema.json and/or schemas/install-modules.schema.json
4. Update scripts/lib/install-manifests.js and install-targets/*.js
5. Update or add tests for new install target

**Files typically involved**:
- `.*/install.js`
- `.*/install.sh`
- `.*/uninstall.js`
- `.*/uninstall.sh`
- `manifests/install-modules.json`
- `schemas/ecc-install-config.schema.json`
- `schemas/install-modules.schema.json`
- `scripts/lib/install-manifests.js`
- `scripts/lib/install-targets/*.js`
- `tests/lib/install-targets.test.js`

**Example commit sequence**:
```
Add or update install scripts (install.js, install.sh, uninstall.js, uninstall.sh) in a target directory
Update manifests/install-modules.json
Update schemas/ecc-install-config.schema.json and/or schemas/install-modules.schema.json
Update scripts/lib/install-manifests.js and install-targets/*.js
Update or add tests for new install target
```

### Ci Hook Or Script Fix

Fixes, updates, or refactors CI/CD hooks, scripts, or related lockfiles for build/test automation.

**Frequency**: ~2 times per month

**Steps**:
1. Edit hooks/hooks.json and/or scripts/hooks/*.js or .sh
2. Update or add tests in tests/hooks/
3. Update lockfiles (package-lock.json, yarn.lock, Cargo.lock) if dependencies change
4. Commit with a fix or perf message

**Files typically involved**:
- `hooks/hooks.json`
- `scripts/hooks/*.js`
- `scripts/hooks/*.sh`
- `tests/hooks/*.test.js`
- `package-lock.json`
- `yarn.lock`
- `ecc2/Cargo.lock`

**Example commit sequence**:
```
Edit hooks/hooks.json and/or scripts/hooks/*.js or .sh
Update or add tests in tests/hooks/
Update lockfiles (package-lock.json, yarn.lock, Cargo.lock) if dependencies change
Commit with a fix or perf message
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
