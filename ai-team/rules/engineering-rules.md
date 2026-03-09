# Engineering Rules

These are the default operating rules for the Codex AI Team.

## 1. Plan Before Code

- Use Planner before any multi-file feature, subsystem change, or refactor
- Do not let Builder start from an ambiguous request
- Keep work scoped to the smallest shippable slice

## 2. Architecture Before Expansion

- Use Architect before changing module boundaries, APIs, or data models
- Freeze interfaces before implementation where possible
- Reduce scope instead of shipping vague architecture

## 3. Tests Protect Behavior

- For behavior changes, add or update tests before or during implementation
- Cover happy path, error path, and edge cases
- Prefer deterministic tests over brittle, environment-coupled tests

## 4. Review Every Change

- Reviewer must inspect the implementation after Builder finishes a slice
- High-risk areas need explicit checks for security, performance, and regression risk
- If Reviewer finds a blocker, return to Builder before continuing

## 5. Reuse Beats Reinvention

- Inspect the existing repository before introducing new abstractions
- Prefer established project patterns when they are sound
- Do not create a framework when a focused module will do

## 6. Keep Boundaries Explicit

- Validate inputs at system boundaries
- Make error handling explicit
- Prefer typed or schema-validated contracts over implicit conventions

## 7. Favor Immutability and Small Modules

- Prefer creating new objects over mutating shared state
- Keep files cohesive and focused
- Split oversized functions or modules before they become hard to reason about

## 8. Security Is Non-Negotiable

- Never hardcode secrets
- Validate external input
- Use safe query and rendering patterns
- Do not leak internal details in user-facing errors

## 9. Work Incrementally

- Large codebases should be changed in narrow, verifiable slices
- Avoid mixing refactors, features, and unrelated cleanup in the same pass
- Preserve rollback paths for risky changes

## 10. Leave a Usable Record

- Every stage must produce structured output another stage can consume
- Record assumptions, constraints, open questions, and next actions
- Prefer precise summaries over vague status updates
