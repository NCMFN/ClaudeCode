# Design New System Workflow

Use this workflow for a greenfield product, service, platform, or major net-new capability.

## Inputs

- Product or platform goal
- Target users
- Constraints
- Tech stack preferences, if any

## Orchestration

1. Load both rules files.
2. Run `ai-team/agents/planner.md`.
   - Produce the delivery roadmap, milestones, risks, and unknowns.
3. Run `ai-team/agents/architect.md`.
   - Produce the system architecture, services, modules, API contracts, and data structures.
4. Run `ai-team/agents/builder.md`.
   - Scaffold the repository or implement the first milestone.
   - Add tests for the initial slice.
5. Run `ai-team/agents/reviewer.md`.
   - Audit the foundation for security, architecture fit, and future scalability.

## Default Deliverables

- Project brief
- Architecture package
- Initial repo structure or first working slice
- Review report with next actions
