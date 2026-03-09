# Build Feature Workflow

Use this workflow to implement a new feature in an existing codebase with the Codex AI Team.

## Inputs

- Feature goal
- User value
- Constraints
- Existing repository or module context

## Orchestration

1. Load `ai-team/rules/engineering-rules.md` and `ai-team/rules/architecture-principles.md`.
2. Run `ai-team/agents/planner.md`.
   - Produce milestones, dependencies, risks, and a Planner -> Architect handoff.
3. Run `ai-team/agents/architect.md` using the approved plan.
   - Produce modules, contracts, data structures, and an Architect -> Builder handoff.
4. Run `ai-team/agents/builder.md`.
   - Implement only the first approved milestone unless the user requested full execution.
   - Add tests when behavior changes.
5. Run `ai-team/agents/reviewer.md`.
   - Audit the diff for bugs, architecture drift, performance, and security.
6. If Reviewer reports blockers, loop Builder -> Reviewer until clear.
7. Return:
   - final status
   - files changed
   - tests run
   - remaining risks or next milestones

## Default Controls

- Prefer the smallest shippable slice
- Keep handoffs explicit between stages
- Do not skip architecture when multiple modules are affected
- Do not skip review after implementation

## Large Codebase Mode

If the repository is large:

- Limit the first pass to the smallest affected module group
- Defer unrelated cleanup
- Ask Builder to change a narrow file set per cycle
- Make Reviewer audit only the touched surface plus contract boundaries
