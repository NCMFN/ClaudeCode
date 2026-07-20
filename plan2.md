1. **Phase 1 Ingestion**: Add reservoir sampling for benign events over 3M lines to simulate a broader time range, inject known redteam events. Log the synthetic imbalance.
2. **Phase 3 Modeling**:
   - Implement `GroupShuffleSplit` for Train/Val/Test (60/20/20).
   - Train base models on Train. Train Meta on Train.
   - Select threshold using Val set (fixing the leakage).
   - Implement `StratifiedGroupKFold` (5 folds) to get cross-validation metrics for significance testing.
3. **Phase 4 Adversarial**:
   - Evasion: Perturb test set, measure PR-AUC.
   - Poisoning: Flip 5% of labels in Train, retrain Meta, measure on Test.
   - Dist-Shift: Train on early days, measure on late days.
4. **Phase 5 Evaluation**:
   - Compute metrics using the Val-selected threshold.
   - Significance testing: Use `scipy.stats.wilcoxon` on fold scores.
   - Ablation: Retrain XGBoost after removing specific feature groups, measure PR-AUC.
   - Complexity: Use `time.perf_counter()` to measure real latency.
5. **Revision Log**: Honestly document everything, including NOT_COMPUTED if things timeout, and noting the synthetic imbalance ratio.
