# Design System Workflow

Use this workflow to design or redesign a subsystem inside an existing product before major implementation starts.

## Inputs

- Subsystem goal
- Existing system context
- Constraints
- Interfaces that must remain compatible

## Orchestration

1. Load both rules files.
2. Run `ai-team/agents/planner.md`.
   - Define the subsystem scope, dependencies, and phased rollout plan.
3. Run `ai-team/agents/architect.md`.
   - Produce the subsystem architecture, module map, contracts, and migration or rollout plan.
4. Run `ai-team/agents/builder.md` only if the user wants scaffolding or the first implementation slice.
5. Run `ai-team/agents/reviewer.md`.
   - Audit the design or scaffold for maintainability, risk, and compatibility.

## Required Outputs

- Subsystem architecture
- Integration boundaries
- Migration plan
- First implementation slice or scaffold, if requested
