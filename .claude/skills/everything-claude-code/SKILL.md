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
feat: add everything-claude-code ECC bundle (.claude/commands/add-or-update-command.md)
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

### Add New Skill Or Agent

Adds a new agent or skill to the codebase, including documentation and configuration.

**Frequency**: ~3 times per month

**Steps**:
1. Create a new SKILL.md or agent markdown file in the appropriate directory (skills/ or agents/).
2. Optionally add supporting files such as YAML configs or example usage.
3. Update relevant index or manifest files if needed.

**Files typically involved**:
- `skills/*/SKILL.md`
- `agents/*.md`
- `.agents/skills/*/SKILL.md`
- `.claude/skills/*/SKILL.md`

**Example commit sequence**:
```
Create a new SKILL.md or agent markdown file in the appropriate directory (skills/ or agents/).
Optionally add supporting files such as YAML configs or example usage.
Update relevant index or manifest files if needed.
```

### Add Or Update Command

Adds or updates a command markdown file, defining new CLI commands or workflows.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update a markdown file in the commands/ or .claude/commands/ directory.
2. Document the command's usage, arguments, and output.
3. Optionally update related documentation or index files.

**Files typically involved**:
- `commands/*.md`
- `.claude/commands/*.md`

**Example commit sequence**:
```
Create or update a markdown file in the commands/ or .claude/commands/ directory.
Document the command's usage, arguments, and output.
Optionally update related documentation or index files.
```

### Add Or Update Install Target

Adds or updates an install target, including scripts, schemas, and manifest entries for new integrations.

**Frequency**: ~2 times per month

**Steps**:
1. Add new install scripts (e.g., install.sh, install.js) in a dedicated directory.
2. Update manifests/install-modules.json and relevant schema files.
3. Update or add code in scripts/lib/install-manifests.js and install-targets/*.
4. Add or update tests for install targets.

**Files typically involved**:
- `manifests/install-modules.json`
- `schemas/ecc-install-config.schema.json`
- `schemas/install-modules.schema.json`
- `scripts/lib/install-manifests.js`
- `scripts/lib/install-targets/*.js`
- `tests/lib/install-targets.test.js`
- `.*/install.*`

**Example commit sequence**:
```
Add new install scripts (e.g., install.sh, install.js) in a dedicated directory.
Update manifests/install-modules.json and relevant schema files.
Update or add code in scripts/lib/install-manifests.js and install-targets/*.
Add or update tests for install targets.
```

### Update Hooks Or Hook Scripts

Updates hook configuration or scripts to change automation, formatting, or session management behaviors.

**Frequency**: ~3 times per month

**Steps**:
1. Edit hooks/hooks.json to add or modify hook definitions.
2. Update or add scripts in scripts/hooks/ or tests/hooks/.
3. Optionally update related shell scripts or adapters.

**Files typically involved**:
- `hooks/hooks.json`
- `scripts/hooks/*.js`
- `scripts/hooks/*.sh`
- `tests/hooks/*.test.js`

**Example commit sequence**:
```
Edit hooks/hooks.json to add or modify hook definitions.
Update or add scripts in scripts/hooks/ or tests/hooks/.
Optionally update related shell scripts or adapters.
```

### Dependency Bump Github Actions

Automated or manual updates to GitHub Actions dependencies for CI/CD workflows.

**Frequency**: ~4 times per month

**Steps**:
1. Update version numbers in .github/workflows/*.yml files for specific actions.
2. Commit with a standardized message indicating the dependency and new version.

**Files typically involved**:
- `.github/workflows/*.yml`

**Example commit sequence**:
```
Update version numbers in .github/workflows/*.yml files for specific actions.
Commit with a standardized message indicating the dependency and new version.
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
