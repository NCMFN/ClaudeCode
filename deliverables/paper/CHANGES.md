# Changes from Legacy Pipeline
1. Removed all synthetic data generation and "illustrative" padding.
2. Replaced the flawed naive sampling strategy with a robust time-stratified approach.
3. Implemented strictly causal feature engineering, removing expanding global statistics.
4. Introduced chronological evaluation protocols (P3, P4) with purge gaps, replacing random splits.
5. Added leakage probes (time-only baseline, ablations) to audit metrics.
6. Enforced rigorous linting of figures to prevent placeholder or text-only artefacts.
