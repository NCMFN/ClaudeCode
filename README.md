# Temporal Leakage in Insider-Threat Evaluation

This repository implements a Temporal-Leakage Audit and Chronological-Evaluation Study on the LANL dataset.
It explores the effects of experimental setup (sampling and time leakage) on model evaluation.

## Real vs Protocol Only Modes
- **REAL Mode**: Triggered when the full LANL dataset (including the actual redteam.txt.gz) can be successfully obtained and ingested.
- **PROTOCOL_ONLY Mode**: If the ground truth data cannot be fully obtained or parsed, the pipeline falls back to this mode. In this mode, no performance metrics are computed, no results are claimed, and the manuscript is rendered as a proposed protocol only.

## Data Sources
- LANL dataset landing page: https://csr.lanl.gov/data/cyber1/
- See `docs/source_verification.md` for URL verifications.
