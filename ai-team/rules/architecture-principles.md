# Architecture Principles

These principles guide Architect, constrain Builder, and give Reviewer a stable baseline.

## 1. Explicit Module Boundaries

- Each module should have a clear responsibility
- Cross-module communication should happen through defined interfaces
- Hidden coupling is architecture debt

## 2. Stable Contracts

- APIs, events, and data models should be explicit
- Validation and error behavior belong in the contract
- Backward compatibility should be intentional, not accidental

## 3. Incremental Delivery

- Prefer designs that can ship in milestones
- Avoid big-bang dependencies where nothing works until everything lands
- Make partial progress useful and testable

## 4. Simple Before Clever

- Choose the simplest design that meets current constraints
- Do not overfit for hypothetical scale
- Add abstraction only when it reduces present complexity

## 5. Security at the Boundary

- Authenticate and authorize before sensitive actions
- Validate input at entry points
- Separate trusted internal data from untrusted external data

## 6. Data With Invariants

- Every important data structure should define its invariants
- Persistence models and transfer models should be distinct when needed
- Data ownership should be clear

## 7. Failure-Aware Design

- Design for retries, errors, and degraded modes where needed
- Make error states observable and recoverable
- Avoid silent failure paths

## 8. Performance by Budget

- Define the hot paths before optimizing
- Keep network hops, synchronous blocking, and unbounded queries visible
- Use instrumentation before guessing at bottlenecks

## 9. Operability Matters

- Migrations, rollout order, and rollback paths are part of the design
- Monitoring and debugging hooks should be considered for critical paths
- Reviewer should be able to reason about what changed and why

## 10. Architecture Drives Review

- Reviewer checks code against the agreed architecture, not personal preference
- If implementation violates a contract, either fix the code or revise the architecture explicitly
