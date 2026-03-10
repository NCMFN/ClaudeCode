# New Project Prompt Template

Copy this prompt into Codex when starting a brand-new software project.

```text
Follow these files as the operating system for this project:

- /path/to/repo/ai-team/workflows/start-new-project.md
- /path/to/repo/ai-team/rules/engineering-rules.md
- /path/to/repo/ai-team/rules/architecture-principles.md

Act as a four-stage AI engineering team:
1. Planner
2. Architect
3. Builder
4. Reviewer

Project goal: [What are we building?]
Target users: [Who is this for?]
Constraints: [Timeline, compliance, platform, budget, integrations, deployment limits]
Tech stack preferences: [Preferred stack or "choose for me"]

Execution rules:
- Run the stages in order: Planner -> Architect -> Builder -> Reviewer
- Keep each stage output structured and include explicit handoff blocks
- Keep scope to milestone 1 or the first working slice unless I ask for full implementation
- Builder should write tests for new or changed behavior
- Reviewer should focus on bugs, architecture compliance, security, and performance
- If Reviewer finds blockers, loop back to Builder and re-review before moving on

Required final output:
- Project summary
- Milestone 1 plan
- Architecture overview
- Initial scaffold or first implementation slice
- Review findings
- Next recommended milestone
```

## Example

```text
Follow these files as the operating system for this project:

- /Users/snehaprajapati/Desktop/Sneha_Develop/everything-claude-code/ai-team/workflows/start-new-project.md
- /Users/snehaprajapati/Desktop/Sneha_Develop/everything-claude-code/ai-team/rules/engineering-rules.md
- /Users/snehaprajapati/Desktop/Sneha_Develop/everything-claude-code/ai-team/rules/architecture-principles.md

Act as a four-stage AI engineering team:
1. Planner
2. Architect
3. Builder
4. Reviewer

Project goal: Build a SaaS app for tracking vendor contracts and renewal risk.
Target users: Procurement teams at mid-sized companies.
Constraints: Web app, 6-week MVP, audit trail required, SSO later, small engineering team.
Tech stack preferences: Next.js + TypeScript + Postgres, or choose a better option if needed.

Execution rules:
- Run the stages in order: Planner -> Architect -> Builder -> Reviewer
- Keep each stage output structured and include explicit handoff blocks
- Keep scope to milestone 1 or the first working slice unless I ask for full implementation
- Builder should write tests for new or changed behavior
- Reviewer should focus on bugs, architecture compliance, security, and performance
- If Reviewer finds blockers, loop back to Builder and re-review before moving on

Required final output:
- Project summary
- Milestone 1 plan
- Architecture overview
- Initial scaffold or first implementation slice
- Review findings
- Next recommended milestone
```

## Reuse Notes

- Replace `/path/to/repo` with the actual workspace path.
- If the new repo copies `ai-team/` unchanged, only the path and intake fields need updating.
- For later work, switch from this bootstrap prompt to the workflow that matches the task:
  - `build-feature.md`
  - `debug-issue.md`
  - `debug-system.md`
  - `refactor-module.md`
  - `design-system.md`
