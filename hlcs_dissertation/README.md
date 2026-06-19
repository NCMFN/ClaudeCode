# Hybrid Post-Quantum Commitment Schemes for Latency-Constrained Financial Systems

This repository contains the full implementation, benchmarks, and dissertation generator for the Hybrid Hash-Lattice Commitment Scheme (HLCS).

## Setup

```bash
pip install -r requirements.txt
```

## Running

1. Run benchmarks in `src/benchmarks/`.
2. Run attacks in `src/attacks/`.
3. Run extended benchmarks in `src/extended/`.
4. Generate figures and tables using `src/dissertation/generate_all_figures.py` and `src/dissertation/generate_all_tables.py`.
5. Build the dissertation using `src/dissertation/build_dissertation.py`.
6. Run `check_validation.py` to verify correctness.
