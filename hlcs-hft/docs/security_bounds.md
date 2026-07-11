# Latency-Adaptive Security Bounds

This document derives the security bounds for our scheme under different latency constraints.

## Target Configuration
Per `config/experiment.toml`, we use:
- **Lattice Security Category**: 3
- **LWE Dimension**: 768

## Hardness Decay Function f(τ)
Let τ be the latency parameter. As latency decreases, the attacker's time to process an order decreases. This provides a natural limit on the amount of computation an attacker can perform before the order must be finalized.

The effective security parameter λ' can be expressed as:
λ' = λ * f(τ)

For our system, we define f(τ) = 1.0 for τ >= 1ms. For τ < 1ms, the latency constraint is tighter than the computational constraint, effectively increasing the hardness per unit time. We model this as:
f(τ) = max(1.0, 1.0 / sqrt(τ))

## Reduction to SIS
The security of our lattice commitment scheme relies on the Short Integer Solution (SIS) problem. We assume that finding a collision in our commitment function is at least as hard as solving SIS in dimension 768.

This reduction is valid because any collision in the commitment scheme translates to finding a short non-zero vector in the corresponding lattice defined by the commitment parameters. Given our parameter selection (category 3), finding such a vector is computationally intractable within the given latency bounds, as demonstrated by the latency benchmarks in `results/tables/obj1_latency.csv`.
