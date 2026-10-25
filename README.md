# Temporal Leakage Audit on the LANL Red-Team Dataset

This repository contains a research-grade ML pipeline that conducts a leakage-aware chronological evaluation on the official LANL cyber-security authentication dataset.

It is designed as an **evaluation-methodology and temporal-leakage study**, NOT as a validated insider-threat detector. The events represent a specific red-team exercise, which is distinct from actual insider behaviour and should not be conflated.

## Features
- **Strict Chronological Splitting:** Implements rolling-origin validation with a purge gap to prevent temporal leakage.
- **Time-Stratified Sampling:** Mitigates the temporal biases seen in legacy approaches where benign and malicious events occupied disjoint time ranges.
- **Causal Feature Engineering:** Prevents future-data leakage in feature computation.

## Execution
```bash
pip install -r requirements.txt
python src/run_pipeline.py
```
