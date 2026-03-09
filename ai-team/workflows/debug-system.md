# Debug System Workflow

Use this workflow for cross-module failures, distributed bugs, recurring incidents, or production reliability issues.

## Inputs

- Incident summary
- Observed symptoms
- Suspected systems or services
- Production constraints and blast radius

## Orchestration

1. Load both rules files.
2. Run `ai-team/agents/planner.md`.
   - Map symptoms to candidate components, missing telemetry, and investigation order.
3. Run `ai-team/agents/architect.md`.
   - Model the failing system, trust boundaries, bottlenecks, and safe intervention points.
4. Run `ai-team/agents/builder.md`.
   - Add instrumentation if needed.
   - Reproduce or approximate the failure.
   - Implement the smallest safe fix or containment step.
5. Run `ai-team/agents/reviewer.md`.
   - Focus on regression risk, security exposure, rollout safety, and operational follow-up.
6. Repeat Builder -> Reviewer until the system is stable enough to ship.

## Required Outputs

- Failure model
- Root cause or strongest hypothesis
- Mitigation or fix
- Validation evidence
- Follow-up hardening work
