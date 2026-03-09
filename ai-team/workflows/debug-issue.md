# Debug Issue Workflow

Use this workflow for a localized bug, failing test, broken integration, or reproducible regression.

## Inputs

- Symptom or error
- Expected behavior
- Reproduction steps
- Constraints on rollback, uptime, or release timing

## Orchestration

1. Load `ai-team/rules/engineering-rules.md`.
2. Run `ai-team/agents/planner.md`.
   - Convert the symptom into hypotheses, affected components, reproduction tasks, and a fix order.
3. Run `ai-team/agents/architect.md` only for the scope needed to fix the issue safely.
   - Define invariants, affected boundaries, and what must not change.
4. Run `ai-team/agents/builder.md`.
   - Reproduce the issue.
   - Write or update a failing test when possible.
   - Implement the minimal fix.
5. Run `ai-team/agents/reviewer.md`.
   - Verify the fix, check regression risk, and confirm architecture compliance.
6. If blockers remain, loop Builder -> Reviewer.

## Expected Deliverables

- Root-cause summary
- Fix summary
- Regression protection
- Remaining edge cases or monitoring needs
