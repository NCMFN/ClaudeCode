1. **Graph Features Fix**: Update `src/phase2_features.py` to use `.sample(n=min(50000, len(df)), random_state=42)` instead of `.head(10000)` to ensure true unbiased edge sampling.
2. **Snapshot Pass 3 Tables**: Copy `outputs/tables/*.csv` to `outputs/tables/_pass3_snapshot/`.
3. **Execute Fresh Run End-to-End**: Run `src/run_pipeline.py`. Log row/column counts dynamically during execution.
4. **Compare Outputs**: Write `verify_fresh_run.py` to compare new `outputs/tables` to `_pass3_snapshot` using `filecmp` or pandas diffs to mathematically prove the run generated fresh values. Append differences to `outputs/revision_log.md`.
5. **Phase 6 True Artifacts**: Replace `aux_fig_*.png` placeholders with real, descriptive plotting routines (ROC curves, Calibration plots, CV variance plots, Latency scatter, etc.) to natively generate exactly 20 distinct domain-specific PNGs and 20 CSVs.
6. **Update revision_log.md**: Add Pass #4 summary with proof of run.
