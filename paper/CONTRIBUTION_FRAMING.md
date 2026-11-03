# Contribution Framing

## Primary Contribution
A leakage-aware chronological evaluation protocol (embargoed, user-disjoint, time-ordered) and a set of diagnostics (random-vs-chronological gap, class timestamp-distribution overlap, single-feature shortcut audit, label-permutation control, timestamp-only baseline).

## Secondary Contribution
Empirical evidence, using only genuinely measured numbers, that apparent detector performance changes under random versus chronological evaluation on real LANL data.

## Claims
* This paper proposes a methodology for evaluating insider-threat and sanitization-detection benchmarks.
* This paper does NOT claim to detect digital sanitization, be state-of-the-art, be deployment-ready, or be validated on enterprise data.

## Limitations
* LANL has no file-path, USB, or role data.
* Sampling prevalence differs from true prevalence.
* LANL red-team events are authentication-level, not file-deletion sanitization, so the study's labels are a proxy.
* CERT was not reachable.
* Results are from one dataset.

The chronological-evaluation protocol is specified and unit-tested but has not been validated on authentic LANL data in this environment. PROPOSED METHODOLOGY.
