1. **Fix Data Ingestion (CERT Dataset):**
   - In `src/phase1_ingestion.py`, download the CERT subset from a direct raw link or simulate it *only if specifically allowed*. Wait, the prompt says "do not fabricate results". I need to download a real dataset. I will find a direct raw link to a CERT r6.2 CSV file or use `curl` to fetch it.
   - Combine with LANL.

2. **Remove Label Fabrication & Fix Recall:**
   - In `src/phase3_modeling.py`, remove the `if len(np.unique(y_test)) == 1:` artificial label injection.
   - Ensure the `max_records` in `phase1_ingestion.py` is large enough to naturally capture malicious events from `redteam.txt`. Currently it only fetches the first 50,000 LANL records. I should stream until I hit at least some redteam events, or load specific known malicious indices.
   - Adjust classification thresholds (e.g., predict probabilities, use a lower threshold) to ensure non-zero recall for the minority class.

3. **Implement Advanced Baselines (GNN & Transformers):**
   - In `src/phase3_modeling.py` (or a new phase), implement a PyTorch-based Graph Neural Network (e.g., GCN or GraphSAGE) using `torch_geometric` or just a PyTorch manual implementation on the authentication graph.
   - Implement a Transformer encoder (e.g., TabNet or a standard PyTorch Transformer) instead of or alongside LSTM.

4. **Fix Adversarial Test Leakage & Add Scenarios:**
   - In `src/phase4_adversarial.py`, implement multiple evasion scenarios (e.g., timing delays, randomized target selection).
   - Fix the train/test leakage: Make sure adversarial training uses *only* the training set, not the test set, and evaluate on a held-out test set.

5. **Significance Testing & Ablation Study:**
   - In `src/phase5_evaluation.py`, implement statistical significance testing (e.g., paired t-test or Wilcoxon signed-rank test on model predictions/probabilities).
   - Add an ablation study: Train and evaluate models by dropping specific feature subsets (e.g., temporal, graph, entropy) to measure their impact.

6. **Inference-Time Analysis:**
   - Measure and report the inference latency (milliseconds per event) for the pipeline.
   - Add these metrics to the output tables.

7. **Consolidate and Execute:**
   - Ensure `run_pipeline.py` executes all phases and saves *all* required figures and tables (now including ablation results, significance results, complexity, multiple adversarial scenarios).
   - Update `downloads.md`.
   - Run tests.

8. **Pre-commit and Submit:**
   - Run pre-commit instructions.
   - Call the `submit` tool.
