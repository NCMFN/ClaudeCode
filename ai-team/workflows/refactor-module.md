# Refactor Module Workflow

Use this workflow when improving structure, reducing complexity, or changing module boundaries without changing intended behavior.

## Inputs

- Refactor goal
- Current pain points
- Invariants that must stay true
- Performance or compatibility constraints

## Orchestration

1. Load both rules files.
2. Run `ai-team/agents/planner.md`.
   - Identify the current problems, risks, and the smallest safe slices.
3. Run `ai-team/agents/architect.md`.
   - Define the target module boundaries, contracts, and migration path.
4. Run `ai-team/agents/builder.md`.
   - Add regression tests first where coverage is weak.
   - Refactor in small, reversible steps.
5. Run `ai-team/agents/reviewer.md`.
   - Check for behavior drift, hidden coupling, and unnecessary complexity.
6. Iterate Builder -> Reviewer until the refactor is clean.

## Required Outputs

- Before vs after module design
- Files changed
- Regression coverage added
- Residual debt that was intentionally left out of scope
