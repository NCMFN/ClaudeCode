```markdown
# everything-claude-code Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches the core development patterns, coding conventions, and collaborative workflows used in the `everything-claude-code` repository. The project is JavaScript-based (no framework), with a focus on modular agents, skills, and commands, and a strong emphasis on documentation and catalog synchronization. It uses conventional commits, mixed export styles, and a structured approach to adding new features, language support, and infrastructure.

## Coding Conventions

- **File Naming:**  
  Use `camelCase` for JavaScript files and directories.  
  *Example:*  
  ```
  scripts/myScript.js
  agents/buildResolver.md
  ```

- **Import Style:**  
  Use relative imports for modules.  
  *Example:*  
  ```js
  const utils = require('../utils/helper');
  import { doThing } from './doThing';
  ```

- **Export Style:**  
  Mixed: both CommonJS (`module.exports`) and ES6 (`export`) are used.  
  *Example (CommonJS):*  
  ```js
  module.exports = function main() { /* ... */ };
  ```
  *Example (ES6):*  
  ```js
  export function main() { /* ... */ }
  ```

- **Commit Messages:**  
  Use [Conventional Commits](https://www.conventionalcommits.org/):  
  - Prefixes: `fix`, `feat`, `docs`, `chore`
  - Example:  
    ```
    feat: add Dart language support to catalog
    fix: correct agent registration in install-modules.json
    ```

## Workflows

### Add New Agent or Skill
**Trigger:** When introducing a new agent or skill for a domain, workflow, or integration  
**Command:** `/add-skill`

1. Create a new markdown file in `agents/` or `skills/` (e.g., `skills/mySkill/SKILL.md`).
2. Optionally add supporting files (e.g., `references/`, `scripts/`, agent subfiles).
3. Update `manifests/install-modules.json` if registration is needed.
4. Update `AGENTS.md` and/or `README.md` to reflect the new agent/skill.
5. Add or update test files if needed.

*Example:*
```bash
cp skills/template/SKILL.md skills/mySkill/SKILL.md
# Edit and register as needed
```

---

### Add New Command or Workflow
**Trigger:** When adding a new CLI command, workflow, or process  
**Command:** `/add-command`

1. Create a new command markdown file in `commands/` or `.opencode/commands/`.
2. If part of a workflow, create/update orchestrator scripts or shell files.
3. Update `AGENTS.md` and/or `README.md` to document the new command/workflow.
4. If part of a skill, update the corresponding `SKILL.md`.

*Example:*
```bash
touch commands/myNewCommand.md
# Document and implement the command
```

---

### Language Support Pack
**Trigger:** When adding first-class support for a new programming language  
**Command:** `/add-language-support`

1. Create rules in `rules/<language>/*.md` (coding style, patterns, security, testing, etc.).
2. Add agent(s) in `agents/` (e.g., `build-resolver`, `reviewer`).
3. Add commands in `commands/` (e.g., `dart-build.md`).
4. Add skill(s) in `skills/<language>-patterns/SKILL.md`.
5. Update `manifests/install-modules.json` to register the language module.
6. Update `AGENTS.md` and `README.md` to reflect new language support.

*Example:*
```bash
mkdir rules/go
touch rules/go/coding-style.md
cp skills/template/SKILL.md skills/go-patterns/SKILL.md
```

---

### Add or Update MCP Server
**Trigger:** When integrating or updating an MCP (Model Context Protocol) server  
**Command:** `/add-mcp-server`

1. Add or update entry in `mcp-configs/mcp-servers.json`.
2. Update related skill documentation if needed.
3. Pin or update server versions for security.
4. If required, update `.mcp.json` for local MCP config.
5. Document the new server in `README.md` or `AGENTS.md` if relevant.

---

### Dependency Bump via Dependabot
**Trigger:** When updating dependencies for security, features, or maintenance  
**Command:** `/bump-dependency`

1. Update version in `package.json` or relevant workflow YAML.
2. Update lockfile (`yarn.lock` or `package-lock.json`).
3. Commit with a standardized message referencing the dependency and version.
4. If a GitHub Action, update the relevant `.github/workflows/*.yml` file(s).

*Example commit message:*
```
chore: bump lodash from 4.17.21 to 4.17.22
```

---

### Post PR Review Fixup
**Trigger:** When a pull request receives review feedback requiring changes  
**Command:** `/fix-pr-feedback`

1. Edit files to address reviewer comments (code, docs, config).
2. Clarify or correct documentation as needed.
3. Update related tests if required.
4. Commit with a message referencing the PR and review feedback.

---

### Harden or Fix Hooks and Scripts
**Trigger:** When fixing bugs, security issues, or platform problems in hooks/scripts  
**Command:** `/fix-hook`

1. Edit `scripts/hooks/*.js` or `hooks/hooks.json` to fix logic or issues.
2. Update related shell scripts or adapters.
3. Add or update test files for the affected hook/script.
4. Document changes in the commit message, referencing the issue or PR.

---

### Catalog Count Sync
**Trigger:** When agents, skills, or commands are added/removed and documentation needs updating  
**Command:** `/sync-catalog-counts`

1. Update agent/skill/command counts in `README.md` and `AGENTS.md`.
2. Optionally update install manifests or other catalog files.
3. Commit with a message referencing the count update.

---

## Testing Patterns

- **Test Framework:** Unknown (no framework detected), but tests are in `*.test.js` files.
- **Test File Pattern:**  
  All test files should be named with `.test.js` suffix and placed alongside the code or in a `tests/` directory.

*Example:*
```
tests/mySkill.test.js
scripts/hooks/myHook.test.js
```

- **Test Example:**
  ```js
  // tests/mySkill.test.js
  const mySkill = require('../skills/mySkill');
  test('should perform the skill correctly', () => {
    expect(mySkill.doSomething()).toBe(true);
  });
  ```

## Commands

| Command                | Purpose                                                      |
|------------------------|--------------------------------------------------------------|
| /add-skill             | Add a new agent or skill to the codebase                    |
| /add-command           | Introduce a new command or workflow                         |
| /add-language-support  | Add comprehensive support for a new programming language     |
| /add-mcp-server        | Add or update MCP server configurations                     |
| /bump-dependency       | Update dependencies via Dependabot or manually               |
| /fix-pr-feedback       | Apply fixes from code review feedback                       |
| /fix-hook              | Harden or fix lifecycle hooks and scripts                   |
| /sync-catalog-counts   | Synchronize agent/skill/command counts in documentation     |
```
