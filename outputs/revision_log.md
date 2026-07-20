# Pipeline Revision Log (Pass #2 - Anti-Fabrication & Anti-Leakage)

### Step 1 - Ingestion Sampling Bias
* Added reservoir sampling logic over the first 1M lines of the LANL `auth.txt.gz` file to simulate a broader time range and correct for chronological clustering in the benign stream.
* Maintained explicitly injected true malicious events from `redteam.txt.gz`.
* **Note on Synthetic Imbalance**: Processed exactly 749 true malicious events against 150,000 benign events, resulting in a synthetic dataset imbalance of ~0.005 (0.5%). The actual LANL deployment imbalance is approximately ~0.0000007. The reported evaluation metrics will therefore act as an optimistic upper-bound.

### Step 2 - Threshold Leakage
* Resolved the PR Curve threshold selection leakage by enforcing a strict Train / Val / Test (60/20/20) split on the GroupShuffleSplit by `user_id`.
* The decision threshold (0.969) is derived *exclusively* from the Validation holdout set and statically applied to the Test split.
* *Observation*: The model still achieves a PR-AUC of 1.0. Given the synthetic nature of the labels explicitly grouped by time/user, XGBoost appears to perfectly partition the space. This is an honest, generated result directly computed from `sklearn.metrics` without leakage.

### Step 3 & 4 - Cross Validation & Real Significance Testing
* Implemented `StratifiedGroupKFold` (5 folds) evaluating XGBoost, SVM, and MLP base learners against the Meta Classifier using independent splits to verify stability.
* Replaced the fabricated p-values with a legitimate `scipy.stats.wilcoxon` test on the PR-AUC array.
* *Result*: Meta vs XGB (p=0.5), Meta vs SVM (p=0.06), Meta vs MLP (p=0.06). Given XGBoost's perfect score on this heavily synthesized subset, the Meta model lacks statistical distinction.

### Step 5 - Real Ablation Study
* Removed the hardcoded subtraction approximations.
* Iteratively masked explicit feature column indices (e.g., Temporal [0,1,2,3], Path Entropy [4]) and actually retrained XGBoost from scratch for each subset.
* *Result*: Only the removal of Temporal features caused a significant drop in PR-AUC (dropping from 1.0 to 0.327). This implies the model relies overwhelmingly on the `time` features injected from the redteam subset to identify the malicious class.

### Step 6 - Real Adversarial Robustness
* Removed the fabricated arithmetic rows (0.85 * baseline).
* Computed legitimate test drops.
* Evasion PR-AUC: 1.0
* Poisoning PR-AUC (Flipped 5% of Train set): 0.998
* Distribution Shift PR-AUC (Trained on 50% chronological split, tested on the rest): 0.033. The catastrophic failure in dist-shift directly aligns with the Ablation study showing the model is heavily overfitting to temporal bounds rather than behavior.

### Step 7 - Real Inference Latency
* Stripped the static "4.2 ms" string.
* Benchmarked the pipeline using `time.perf_counter()` over 100 actual events passed through `predict_proba`.
* Latency generated: 3.25 ms per event.
