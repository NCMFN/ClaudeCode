# Deception-Resistant Presence Proof (DRPP) - Simulation Framework

This repository contains a Rust-based simulation and analysis framework that empirically validates, extends, and statistically stress-tests the DRPP protocol. This project serves as the Results / Evaluation chapter for a PhD thesis.

## Prerequisites
- Rust stable toolchain (≥ 1.78) via `rustup`

## Build and Run
To build all crates, run all experiments, and generate all figures, tables, and the final report:
```bash
make all
```

To run all unit tests across the workspace:
```bash
make test
```

To clean generated artifacts:
```bash
make clean
```

## Reproducibility
All randomness in this framework is strictly seeded using the `rand::SeedableRng::seed_from_u64` method. The configuration parameters (including the seed) are specified in `experiments/config.toml`. The target output includes exactly 22 figures, 21 tables (in CSV, TeX, and MD formats), and a single consolidated Markdown report (`drpp-research/output/report/results_report.md`).

## Repository Layout
```
drpp-research/
└── output/
    ├── figures/    ← 22 × .png  (individually downloadable)
    ├── tables/     ← 21 × {.csv, .tex, .md}
    └── data/       ← raw CSV trial logs
```

## Index of Outputs
For a comprehensive view of the outputs, refer to the generated `drpp-research/output/report/results_report.md` after running the framework.
