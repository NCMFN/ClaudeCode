1. Re-submit the form at https://csr.lanl.gov/data/cyber1/ and export fresh links as LANL_AUTH_URL and LANL_REDTEAM_URL (or Colab secrets).
2. Run `python3 src/run_pipeline.py --download` to pull the data.
3. Run `python3 src/run_pipeline.py --full` to run the analysis.
4. If interrupted, the pipeline can be resumed from `run_state.json`.
