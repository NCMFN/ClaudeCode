---
name: everything-claude-code-conventions
description: Development conventions and patterns for everything-claude-code. JavaScript project with conventional commits.
---

# Everything Claude Code Conventions

> Generated from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) on 2026-03-18

## Overview

This skill teaches Claude the development patterns and conventions used in everything-claude-code.

## Tech Stack

- **Primary Language**: JavaScript
- **Architecture**: hybrid module organization
- **Test Location**: separate
- **Test Framework**: unknown

## When to Use This Skill

Activate this skill when:
- Making changes to this repository
- Adding new features following established patterns
- Writing tests that match project conventions
- Creating commits with proper message format

## Commit Conventions

Follow these commit message conventions based on 8 analyzed commits.

### Commit Style: Conventional Commits

### Prefixes Used

- `feat`
- `fix`
- `docs`
- `test`

### Message Guidelines

- Average message length: ~67 characters
- Keep first line concise and descriptive
- Use imperative mood ("Add feature" not "Added feature")


*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/add-new-skill-or-agent-doc.md)
```

*Commit message example*

```text
fix: resolve 8 test failures on main (install pipeline, orchestrator, repair) (#564)
```

*Commit message example*

```text
merge: PR #529 — feat(skills): add documentation-lookup, bun-runtime, nextjs-turbopack; feat(agents): add rust-reviewer
```

*Commit message example*

```text
docs(skills): align documentation-lookup with CONTRIBUTING template; add cross-harness (Codex/Cursor) skill copies
```

*Commit message example*

```text
chore(config): governance and config foundation (#292)
```

*Commit message example*

```text
feat: add everything-claude-code ECC bundle (.claude/commands/add-command-or-workflow-doc.md)
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

### Import Style: Mixed Style

### Export Style: Named Exports


*Preferred export style*

```typescript
// Use named exports
export function calculateTotal() { ... }
export const TAX_RATE = 0.1
export interface Order { ... }
```

## Testing

### Test Framework: unknown

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
feat: add everything-claude-code ECC bundle (.claude/identity.json)
feat: add everything-claude-code ECC bundle (.codex/config.toml)
feat: add everything-claude-code ECC bundle (.codex/AGENTS.md)
```

### Add Command Or Workflow Doc

Adds documentation for a new command or workflow to the project.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update a markdown file in .claude/commands/ with the appropriate name (e.g., add-command-or-workflow-doc.md).
2. Commit the new or updated documentation file.

**Files typically involved**:
- `.claude/commands/add-command-or-workflow-doc.md`

**Example commit sequence**:
```
Create or update a markdown file in .claude/commands/ with the appropriate name (e.g., add-command-or-workflow-doc.md).
Commit the new or updated documentation file.
```

### Add Skill Or Agent Doc

Adds documentation for a new skill or agent to the project.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update a markdown file in .claude/commands/ with the appropriate name (e.g., add-new-skill-or-agent-doc.md).
2. Commit the new or updated documentation file.

**Files typically involved**:
- `.claude/commands/add-new-skill-or-agent-doc.md`

**Example commit sequence**:
```
Create or update a markdown file in .claude/commands/ with the appropriate name (e.g., add-new-skill-or-agent-doc.md).
Commit the new or updated documentation file.
```

### Add Team Config

Adds or updates the team configuration for everything-claude-code.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the JSON team config file at .claude/team/everything-claude-code-team-config.json.
2. Commit the new or updated configuration file.

**Files typically involved**:
- `.claude/team/everything-claude-code-team-config.json`

**Example commit sequence**:
```
Create or update the JSON team config file at .claude/team/everything-claude-code-team-config.json.
Commit the new or updated configuration file.
```

### Add Research Playbook

Adds or updates the research playbook documentation.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the markdown file at .claude/research/everything-claude-code-research-playbook.md.
2. Commit the new or updated playbook file.

**Files typically involved**:
- `.claude/research/everything-claude-code-research-playbook.md`

**Example commit sequence**:
```
Create or update the markdown file at .claude/research/everything-claude-code-research-playbook.md.
Commit the new or updated playbook file.
```

### Add Guardrails Doc

Adds or updates the guardrails (rules) documentation.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the markdown file at .claude/rules/everything-claude-code-guardrails.md.
2. Commit the new or updated rules file.

**Files typically involved**:
- `.claude/rules/everything-claude-code-guardrails.md`

**Example commit sequence**:
```
Create or update the markdown file at .claude/rules/everything-claude-code-guardrails.md.
Commit the new or updated rules file.
```

### Add Instincts Config

Adds or updates the instincts configuration for the homunculus agent.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the YAML file at .claude/homunculus/instincts/inherited/everything-claude-code-instincts.yaml.
2. Commit the new or updated instincts configuration.

**Files typically involved**:
- `.claude/homunculus/instincts/inherited/everything-claude-code-instincts.yaml`

**Example commit sequence**:
```
Create or update the YAML file at .claude/homunculus/instincts/inherited/everything-claude-code-instincts.yaml.
Commit the new or updated instincts configuration.
```

### Add Codex Agent Config

Adds or updates configuration for a Codex agent.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the TOML file for the agent in .codex/agents/ (e.g., docs-researcher.toml, reviewer.toml, explorer.toml).
2. Commit the new or updated agent config file.

**Files typically involved**:
- `.codex/agents/docs-researcher.toml`
- `.codex/agents/reviewer.toml`
- `.codex/agents/explorer.toml`

**Example commit sequence**:
```
Create or update the TOML file for the agent in .codex/agents/ (e.g., docs-researcher.toml, reviewer.toml, explorer.toml).
Commit the new or updated agent config file.
```

### Add Codex Agents Index

Adds or updates the index of agents in Codex.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the markdown file at .codex/AGENTS.md.
2. Commit the new or updated agents index file.

**Files typically involved**:
- `.codex/AGENTS.md`

**Example commit sequence**:
```
Create or update the markdown file at .codex/AGENTS.md.
Commit the new or updated agents index file.
```

### Add Identity Config

Adds or updates the identity configuration for everything-claude-code.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the JSON file at .claude/identity.json.
2. Commit the new or updated identity file.

**Files typically involved**:
- `.claude/identity.json`

**Example commit sequence**:
```
Create or update the JSON file at .claude/identity.json.
Commit the new or updated identity file.
```

### Add Skill Doc

Adds or updates documentation for a skill in the agents or claude skills directories.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the SKILL.md file in either .agents/skills/everything-claude-code/ or .claude/skills/everything-claude-code/.
2. Commit the new or updated SKILL.md file.

**Files typically involved**:
- `.agents/skills/everything-claude-code/SKILL.md`
- `.claude/skills/everything-claude-code/SKILL.md`

**Example commit sequence**:
```
Create or update the SKILL.md file in either .agents/skills/everything-claude-code/ or .claude/skills/everything-claude-code/.
Commit the new or updated SKILL.md file.
```

### Add Ecc Tools Config

Adds or updates the ECC tools configuration.

**Frequency**: ~3 times per month

**Steps**:
1. Create or update the JSON file at .claude/ecc-tools.json.
2. Commit the new or updated tools configuration.

**Files typically involved**:
- `.claude/ecc-tools.json`

**Example commit sequence**:
```
Create or update the JSON file at .claude/ecc-tools.json.
Commit the new or updated tools configuration.
```


## Best Practices

Based on analysis of the codebase, follow these practices:

### Do

- Use conventional commit format (feat:, fix:, etc.)
- Write tests using unknown
- Follow *.test.js naming pattern
- Use camelCase for file names
- Prefer named exports

### Don't

- Don't write vague commit messages
- Don't skip tests for new features
- Don't deviate from established patterns without discussion

---

*This skill was auto-generated by [ECC Tools](https://ecc.tools). Review and customize as needed for your team.*
