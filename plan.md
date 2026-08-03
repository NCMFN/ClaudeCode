1. **Initialize Config**: Create `src/config.json` with all required constants (RTT threshold, block sizes, QBER range, etc.) and arbitrary constants for T2K `c1`, `c2`.
2. **Data Ingestion (`src/data_ingest.py`)**: Download WonderNetwork dataset, parse into a chronological RTT time series, validate schema, write `outputs/rtt_source_manifest.csv` and `outputs/manifest.json`.
3. **Policies & QBER (`src/dbs_policy.py`, `src/qber_synth.py`)**: Implement DBS, fixed-large, fixed-small policies. Implement seeded QBER generation.
4. **Key Rate Model (`src/key_rate.py`)**: Implement finite-size-corrected SKR model with unit tests against two hand-computed values.
5. **Simulation (`src/simulate.py`)**: Simulate DBS and fixed policies block-by-block using the RTT trace. Compute SKR, T2K, and failure events. Output to `outputs/results.json`.
6. **Analysis (`src/analysis.py`)**: Perform Wilcoxon signed-rank test and rank-biserial correlation for DBS vs fixed baselines. Save metrics.
7. **Plot Style (`reporting/plot_style.py`)**: Implement `STYLE` dict, `COLORS` dict, and `apply()` function for shared reporting consistency.
8. **Reporting (`reporting/generate_outputs.py`)**: Generate >= 10 figures (DPI=300, tight bounding box) and >= 10 tables (CSVs). Export all requested plots and metrics, generating `outputs/source_manifest.json` and `outputs/paper_assets_manifest.csv`.
9. **Reproducibility Gate**: Run the pipeline twice. Compare `outputs/results.json` and output diff to `outputs/reproducibility_diff.txt`.
10. **Report (`outputs/report.md`)**: Generate the final methodology and summary report.
11. **Pre-commit**: Run `pre_commit_instructions`.
