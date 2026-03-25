---
name: everything-claude-code-conventions
description: Development conventions and patterns for everything-claude-code. JavaScript project with conventional commits.
---

# Everything Claude Code Conventions

> Generated from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) on 2026-03-25

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
- `test`

### Message Guidelines

- Average message length: ~62 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
fix: fold session manager blockers into one candidate
```

*Commit message example*

```text
feat: add 6 gap-closing skills — browser QA, design system, product lens, canary watch, benchmark, safety guard
```

*Commit message example*

```text
docs: add ECC 2.0 reference architecture from competitor research
```

*Commit message example*

```text
perf(hooks): move post-edit-format and post-edit-typecheck to strict-only (#757)
```

*Commit message example*

```text
security: remove supply chain risks, external promotions, and unauthorized credits
```

*Commit message example*

```text
fix(ci): restore validation and antigravity target safety
```

*Commit message example*

```text
Add Kiro steering files, hooks, and scripts (#812)
```

*Commit message example*

```text
Add Kiro skills (18 SKILL.md files) (#811)
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

### Database Migration

Database schema changes with migration files

**Frequency**: ~2 times per month

**Steps**:
1. Create migration file
2. Update schema definitions
3. Generate/update types

**Files typically involved**:
- `migrations/*`

**Example commit sequence**:
```
Add Turkish (tr) docs and update README (#744)
docs(zh-CN): translate code block(plain text) (#753)
fix(install): add rust, cpp, csharp to legacy language alias map (#747)
```

### Feature Development

Standard feature implementation workflow

**Frequency**: ~17 times per month

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
docs: add SECURITY.md, publish agentic security guide, remove openclaw guide
docs: add security guide header image to README
docs: update guide screenshots with current engagement stats
```

### Add New Skill

Adds a new skill to the system, including documentation and implementation files.

**Frequency**: ~2 times per month

**Steps**:
1. Create a new directory under skills/ with the skill name.
2. Add SKILL.md documentation file describing the skill.
3. Add supporting files (e.g., scripts, prompts, fixtures, tests) as needed.
4. Update AGENTS.md and/or README.md to reflect new skill count or catalog.
5. Commit all new files together.

**Files typically involved**:
- `skills/*/SKILL.md`
- `skills/*/scripts/*.py`
- `skills/*/prompts/*.md`
- `skills/*/fixtures/*`
- `skills/*/tests/*.py`
- `AGENTS.md`
- `README.md`

**Example commit sequence**:
```
Create a new directory under skills/ with the skill name.
Add SKILL.md documentation file describing the skill.
Add supporting files (e.g., scripts, prompts, fixtures, tests) as needed.
Update AGENTS.md and/or README.md to reflect new skill count or catalog.
Commit all new files together.
```

### Add Or Update Localization

Adds or updates documentation and skill files for a new or existing language localization.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update files under docs/<lang>/ (e.g., zh-CN, pt-BR, tr).
2. Include translations for agents, commands, skills, rules, and core docs.
3. Update README.md to include new language support or fix language count.
4. Commit all localized files together.

**Files typically involved**:
- `docs/zh-CN/**/*`
- `docs/pt-BR/**/*`
- `docs/tr/**/*`
- `README.md`

**Example commit sequence**:
```
Add or update files under docs/<lang>/ (e.g., zh-CN, pt-BR, tr).
Include translations for agents, commands, skills, rules, and core docs.
Update README.md to include new language support or fix language count.
Commit all localized files together.
```

### Add Or Update Agent Definitions

Adds or updates agent definitions and their documentation.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update .json and .md files under agents/ or .kiro/agents/.
2. Update agent catalog or documentation as needed.
3. Commit all agent files together.

**Files typically involved**:
- `.kiro/agents/*.json`
- `.kiro/agents/*.md`
- `docs/zh-CN/agents/*.md`
- `docs/pt-BR/agents/*.md`
- `docs/tr/agents/*.md`

**Example commit sequence**:
```
Add or update .json and .md files under agents/ or .kiro/agents/.
Update agent catalog or documentation as needed.
Commit all agent files together.
```

### Add Or Update Hooks And Scripts

Adds or modifies project hooks and related scripts, often to enforce new policies or improve workflow automation.

**Frequency**: ~2 times per month

**Steps**:
1. Edit or add files in hooks/ and scripts/hooks/.
2. Update hooks.json to register new hooks.
3. Add or update tests in tests/hooks/.
4. Commit all related files together.

**Files typically involved**:
- `hooks/hooks.json`
- `scripts/hooks/*.js`
- `tests/hooks/*.test.js`

**Example commit sequence**:
```
Edit or add files in hooks/ and scripts/hooks/.
Update hooks.json to register new hooks.
Add or update tests in tests/hooks/.
Commit all related files together.
```

### Add Or Update Kiro Steering And Skills

Adds or updates Kiro steering documentation, scripts, and skills.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update files in .kiro/steering/, .kiro/skills/, .kiro/hooks/, .kiro/scripts/.
2. Commit all related files together.

**Files typically involved**:
- `.kiro/steering/*.md`
- `.kiro/skills/*/SKILL.md`
- `.kiro/hooks/*.kiro.hook`
- `.kiro/scripts/*.sh`

**Example commit sequence**:
```
Add or update files in .kiro/steering/, .kiro/skills/, .kiro/hooks/, .kiro/scripts/.
Commit all related files together.
```

### Add Or Update Install Manifests

Adds or updates install manifest files and supporting scripts/tests for new modules or language support.

**Frequency**: ~2 times per month

**Steps**:
1. Edit manifests/install-modules.json or manifests/install-components.json.
2. Update scripts/lib/install-manifests.js or related scripts.
3. Add or update tests in tests/lib/install-manifests.test.js.
4. Commit all related files together.

**Files typically involved**:
- `manifests/install-modules.json`
- `manifests/install-components.json`
- `scripts/lib/install-manifests.js`
- `tests/lib/install-manifests.test.js`

**Example commit sequence**:
```
Edit manifests/install-modules.json or manifests/install-components.json.
Update scripts/lib/install-manifests.js or related scripts.
Add or update tests in tests/lib/install-manifests.test.js.
Commit all related files together.
```

### Add Or Update Command Docs

Adds or updates documentation for commands, often across multiple languages.

**Frequency**: ~2 times per month

**Steps**:
1. Add or update command markdown files under commands/ or docs/<lang>/commands/.
2. Commit all related files together.

**Files typically involved**:
- `commands/*.md`
- `docs/zh-CN/commands/*.md`
- `docs/pt-BR/commands/*.md`
- `docs/tr/commands/*.md`

**Example commit sequence**:
```
Add or update command markdown files under commands/ or docs/<lang>/commands/.
Commit all related files together.
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
