# Codex AI Team

This package converts the reusable parts of Everything Claude Code into a Codex-native AI engineering workflow.

## Source Mapping

The prompts in this folder were derived from these ECC building blocks:

- Agents: `planner`, `architect`, `tdd-guide`, `code-reviewer`, `security-reviewer`
- Commands: `/plan`, `/tdd`, `/code-review`, `/orchestrate`, `/multi-workflow`
- Skills: `tdd-workflow`, `coding-standards`, `security-review`, `agentic-engineering`, `ai-first-engineering`, `continuous-agent-loop`
- Rules: `CLAUDE.md`, `AGENTS.md`, and `rules/common/*`

## Codex-Native Translation

ECC concept to Codex equivalent:

- `agents/` -> role prompts in `ai-team/agents/`
- `commands/` -> orchestration prompts in `ai-team/workflows/`
- `skills/` -> embedded capability guidance inside agent prompts and rules
- `CLAUDE.md` and common rules -> reusable operating rules in `ai-team/rules/`

This translation accounts for Codex constraints:

- No slash-command runtime: workflows are prompt files instead of commands
- No Claude-style hooks: quality gates are explicit stage instructions
- Single active model: role switching happens through staged prompts and handoffs

## Folder Layout

```text
ai-team/
  agents/
    planner.md
    architect.md
    builder.md
    reviewer.md
  workflows/
    build-feature.md
    debug-issue.md
    debug-system.md
    refactor-module.md
    design-system.md
    design-new-system.md
    start-new-project.md
  rules/
    engineering-rules.md
    architecture-principles.md
```

## Default Team Pipeline

1. Planner turns a request into milestones, risks, and ordered tasks.
2. Architect turns the plan into modules, contracts, data structures, and integration boundaries.
3. Builder implements the approved slice, writes tests when behavior changes, and records integration notes.
4. Reviewer audits the result for bugs, architecture drift, security, and performance issues.

If Reviewer finds blocking issues, loop Builder -> Reviewer until the slice is clear.

## Handoff Contract

Pass this block between stages:

```markdown
## HANDOFF: [Source] -> [Target]

### Objective
[What the next stage is trying to accomplish]

### Decisions
- [Approved decisions only]

### Constraints
- [Technical, product, security, or timeline constraints]

### Open Questions
- [Only unresolved items that materially affect the next stage]

### Next Actions
1. [Smallest useful next step]
2. [Second step if needed]
```

## How To Use

For a new project:

1. Open `ai-team/workflows/start-new-project.md`.
2. Give Codex the project goal, target users, constraints, and tech stack preferences.
3. Let Codex run Planner -> Architect -> Builder -> Reviewer in order.
4. Keep each stage output as a handoff block so the next stage works from explicit context.

For existing codebases:

- New feature: `ai-team/workflows/build-feature.md`
- Bug or regression: `ai-team/workflows/debug-issue.md` or `ai-team/workflows/debug-system.md`
- Refactor: `ai-team/workflows/refactor-module.md`
- New subsystem or greenfield service: `ai-team/workflows/design-system.md` or `ai-team/workflows/design-new-system.md`

## Large Codebase Guidance

When the repository is large, keep the workflow incremental:

- Planner scopes work to the smallest shippable slice
- Architect defines stable contracts before touching implementation
- Builder changes a narrow module set per pass
- Reviewer checks the actual diff first, then surrounding contracts

This keeps Codex effective without requiring the full codebase in every step.
