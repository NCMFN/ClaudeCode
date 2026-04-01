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
feat: add everything-claude-code ECC bundle (.claude/commands/add-new-agent-or-skill.md)
```

*Commit message example*

```text
docs: add Claude Code troubleshooting workarounds
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
fix(security): remove evalview-agent-testing skill — external dependency
```

*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/add-new-install-target.md)
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
- `skills/remotion-video-creation/rules/assets/*`
- `.opencode/*`
- `.opencode/plugins/*`
- `**/*.test.*`

**Example commit sequence**:
```
fix: CI fixes, security audit, remotion skill, lead-intelligence, npm audit (#1039)
chore(deps-dev): bump globals in the minor-and-patch group (#1062)
chore(deps): bump actions/github-script from 7.1.0 to 8.0.0 (#1059)
```

### Add New Install Target

Adds support for a new install target (e.g., CodeBuddy, Gemini) to the system, including scripts, manifests, schemas, and tests.

**Frequency**: ~2 times per month

**Steps**:
1. Create new install scripts (install.js, install.sh, uninstall.js, uninstall.sh) in a dedicated directory (e.g., .codebuddy/ or .gemini/).
2. Add or update a README or documentation file for the new target.
3. Update manifests/install-modules.json to register the new target.
4. Update schemas/ecc-install-config.schema.json and schemas/install-modules.schema.json as needed.
5. Update scripts/lib/install-manifests.js and scripts/lib/install-targets/<target>-project.js.
6. Update or add tests in tests/lib/install-targets.test.js.
7. Update registry or related files if necessary.

**Files typically involved**:
- `manifests/install-modules.json`
- `schemas/ecc-install-config.schema.json`
- `schemas/install-modules.schema.json`
- `scripts/lib/install-manifests.js`
- `scripts/lib/install-targets/*.js`
- `tests/lib/install-targets.test.js`
- `.*/README.md`
- `.*/install.js`
- `.*/install.sh`
- `.*/uninstall.js`
- `.*/uninstall.sh`

**Example commit sequence**:
```
Create new install scripts (install.js, install.sh, uninstall.js, uninstall.sh) in a dedicated directory (e.g., .codebuddy/ or .gemini/).
Add or update a README or documentation file for the new target.
Update manifests/install-modules.json to register the new target.
Update schemas/ecc-install-config.schema.json and schemas/install-modules.schema.json as needed.
Update scripts/lib/install-manifests.js and scripts/lib/install-targets/<target>-project.js.
Update or add tests in tests/lib/install-targets.test.js.
Update registry or related files if necessary.
```

### Add New Skill Or Agent

Adds a new skill or agent to the system, including documentation and registration in manifests.

**Frequency**: ~3 times per month

**Steps**:
1. Create SKILL.md in skills/<skill-name>/ or .claude/skills/<skill-name>/ or .agents/skills/<skill-name>/.
2. Create agent definition(s) in agents/<agent-name>.md if needed.
3. Update manifests/install-modules.json or other relevant manifest files.
4. Add or update documentation (README.md, AGENTS.md, etc.).

**Files typically involved**:
- `skills/*/SKILL.md`
- `.claude/skills/*/SKILL.md`
- `.agents/skills/*/SKILL.md`
- `agents/*.md`
- `manifests/install-modules.json`
- `README.md`
- `AGENTS.md`

**Example commit sequence**:
```
Create SKILL.md in skills/<skill-name>/ or .claude/skills/<skill-name>/ or .agents/skills/<skill-name>/.
Create agent definition(s) in agents/<agent-name>.md if needed.
Update manifests/install-modules.json or other relevant manifest files.
Add or update documentation (README.md, AGENTS.md, etc.).
```

### Add Or Update Command Workflow

Adds or extends user-facing commands (e.g., PRP, santa-loop, GAN harness), often with review/feedback cycles.

**Frequency**: ~2 times per month

**Steps**:
1. Create or update command markdown files in commands/ or .claude/commands/.
2. Add YAML frontmatter, usage, and output sections as per convention.
3. Address review feedback with follow-up fixes (e.g., parameter quoting, API usage, documentation).
4. If needed, update related files (e.g., hooks, tests, AGENTS.md).

**Files typically involved**:
- `commands/*.md`
- `.claude/commands/*.md`

**Example commit sequence**:
```
Create or update command markdown files in commands/ or .claude/commands/.
Add YAML frontmatter, usage, and output sections as per convention.
Address review feedback with follow-up fixes (e.g., parameter quoting, API usage, documentation).
If needed, update related files (e.g., hooks, tests, AGENTS.md).
```

### Add Or Update Opencode Agent

Adds new OpenCode agent prompt files and updates agent registration in opencode.json.

**Frequency**: ~2 times per month

**Steps**:
1. Add new prompt files in .opencode/prompts/agents/*.txt.
2. Update .opencode/opencode.json to register new agents.
3. Update AGENTS.md to reflect new agent count or details.
4. Address review feedback (e.g., remove agents, update documentation).

**Files typically involved**:
- `.opencode/prompts/agents/*.txt`
- `.opencode/opencode.json`
- `AGENTS.md`

**Example commit sequence**:
```
Add new prompt files in .opencode/prompts/agents/*.txt.
Update .opencode/opencode.json to register new agents.
Update AGENTS.md to reflect new agent count or details.
Address review feedback (e.g., remove agents, update documentation).
```

### Add Or Update Hook Orci Script

Implements or fixes hooks and related scripts for formatting, typechecking, session management, or CI integration.

**Frequency**: ~2 times per month

**Steps**:
1. Edit or add scripts in scripts/hooks/ or hooks/hooks.json.
2. Update or add tests in tests/hooks/.
3. Address review feedback (e.g., race conditions, timeouts, path normalization, security).
4. If needed, update related files (e.g., .cursor/hooks/after-file-edit.js, .github/workflows/*).

**Files typically involved**:
- `scripts/hooks/*.js`
- `scripts/hooks/*.sh`
- `hooks/hooks.json`
- `tests/hooks/*.js`
- `.cursor/hooks/*.js`
- `.github/workflows/*.yml`

**Example commit sequence**:
```
Edit or add scripts in scripts/hooks/ or hooks/hooks.json.
Update or add tests in tests/hooks/.
Address review feedback (e.g., race conditions, timeouts, path normalization, security).
If needed, update related files (e.g., .cursor/hooks/after-file-edit.js, .github/workflows/*).
```

### Dependency Update Via Dependabot

Automated or manual update of dependencies (npm packages or GitHub Actions) across multiple workflow files.

**Frequency**: ~4 times per month

**Steps**:
1. Update dependency version in package.json, yarn.lock, or relevant workflow YAML.
2. Update .github/workflows/*.yml to use new action versions.
3. Commit with standardized message referencing the dependency and version bump.

**Files typically involved**:
- `package.json`
- `yarn.lock`
- `package-lock.json`
- `.github/workflows/*.yml`

**Example commit sequence**:
```
Update dependency version in package.json, yarn.lock, or relevant workflow YAML.
Update .github/workflows/*.yml to use new action versions.
Commit with standardized message referencing the dependency and version bump.
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
