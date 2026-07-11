# Hybrid Post-Quantum Commitment Scheme for HFT/FX Systems

This repository contains the software proxy implementation of a high-frequency trading (HFT) ready hybrid lattice+hash commitment scheme, extending the baseline from Adim et al. (2024).

## Project Structure
- `crates/hlcs-core`: Hash and lattice commitment primitives.
- `crates/hlcs-batch`: Merkle-Lattice tree batching and SIS opening logic.
- `crates/hlcs-stark`: zk-STARK based proof migration and malicious security.
- `crates/hlcs-market-sim`: End-to-end slippage simulation using real market data.
- `crates/hlcs-bench-harness`: Top-level orchestrator.

## Reproducibility
All randomized processes use a global seed specified in `config/experiment.toml` (`global_seed = 20260709`).

### Setup and Data Acquisition
To fetch the required sample data (EUR/USD ticks, LOBSTER order books):
```bash
./scripts/fetch_data.sh
```

### Running Tests and Benchmarks
To run the full suite and generate all result tables:

```bash
cargo build --workspace
cargo test --workspace

# Generate Phase 1 metrics
cargo bench -p hlcs-core --bench commit_latency

# Generate Phase 2 metrics
cargo bench -p hlcs-batch --bench batch_throughput

# Generate Phase 3 metrics
cargo bench -p hlcs-stark --bench proof_generation

# Generate Phase 4 metrics
cargo test -p hlcs-market-sim

# Assemble final report
./scripts/generate_report.py
```

The assembled metrics and findings will be placed in `results/final_report.md`.
