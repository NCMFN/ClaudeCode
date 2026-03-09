# Start New Project

Use this prompt to bootstrap a new software project with the Codex AI Team.

## Intake

If any of the following inputs are missing, ask for them before planning:

- project goal
- target users
- constraints
- tech stack preferences

If the user has no stack preference, Architect should choose one and explain why.

## Orchestration

1. Load:
   - `ai-team/rules/engineering-rules.md`
   - `ai-team/rules/architecture-principles.md`
2. Run `ai-team/agents/planner.md`.
   - Convert the idea into milestones, components, risks, and execution order.
3. Run `ai-team/agents/architect.md`.
   - Define the architecture, modules, contracts, and data structures for milestone one.
4. Run `ai-team/agents/builder.md`.
   - Scaffold the repository or implement the first working slice.
   - Add tests when the slice changes behavior or defines critical logic.
5. Run `ai-team/agents/reviewer.md`.
   - Audit the initial build and identify gaps before more implementation begins.
6. Return a final package containing:
   - project summary
   - roadmap
   - architecture
   - initial implementation or scaffold
   - review findings

## Required Behavior

- Keep each stage output structured so the next stage can consume it directly
- Prefer milestone one over trying to build the entire product at once
- Preserve explicit decisions, assumptions, and open questions in the handoff blocks
- If the project is large, stop after the first implemented milestone and propose the next cycle

## Suggested User Prompt

```text
Follow ai-team/workflows/start-new-project.md.

Project goal: [what we are building]
Target users: [who it is for]
Constraints: [timeline, compliance, budget, platform, integrations]
Tech stack preferences: [preferred stack or "choose for me"]
```
