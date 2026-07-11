#!/bin/bash
set -e

echo "Building workspace..."
cargo build --workspace

echo "Running unit tests..."
cargo test --workspace

echo "Running Objective 1 (Latency) benchmarks..."
cargo bench -p hlcs-core --bench commit_latency

echo "Running Objective 2 (Batching) benchmarks..."
cargo bench -p hlcs-batch --bench batch_throughput

echo "Running Objective 3 (STARK) benchmarks..."
cargo bench -p hlcs-stark --bench proof_generation

echo "Running Objective 4 (Market Sim Slippage)..."
cargo test -p hlcs-market-sim

echo "Generating Final Report..."
./scripts/generate_report.py

echo "Done!"
