# Revision Log: Pass #6 (Reviewer-Directed Overhaul)

## Repositioned Contribution
The manuscript has been repositioned based on peer-review feedback. The primary contribution is no longer claimed as an accurate detector of enterprise digital sanitization. Instead, it is presented as a methodological framework for detecting temporal leakage and evaluating generalization in explainable insider-threat detection.

## Key Updates
- **Chronological Split:** Implemented as a first-class evaluation mode alongside the group-split.
- **Sampling Reconstruction:** Added comprehensive tables and figures proving the temporal nature of the dataset's class imbalance.
- **Feature Ablation (Variants A-D):** Systematically tested across multiple splits to demonstrate the collapse of non-temporal features under distribution shift.
- **Adversarial Diagnostics:** Instrumentation added to identify whether attacks exploit the dominant temporal feature (`hour_cos`).
- **Feature Operationalization:** Mapped model inputs strictly to observable behavioral proxies rather than abstract 'sanitization' intent.
- **Limitations Statement:** Not yet completed: cross-dataset validation against CERT r6.2.

## Reproducibility Check
- **Diff Check:** A secondary run with `random_state=42` yielded a 0-byte diff against the first run, proving the pipeline is deterministic and reproducible.

## Artifact Inventory
Over 10 new figures and 10 new tables have been generated in this pass alone, completely replacing or supplementing the previous 20 figures and 20 tables.
