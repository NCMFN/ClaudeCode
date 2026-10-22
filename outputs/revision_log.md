# Revision Pass #6 Log

## Repositioned Contribution
The manuscript has been repositioned. The central contribution is now a **methodological framework for detecting temporal leakage and evaluating generalization in explainable insider-threat detection**, rather than claiming an accurate digital sanitization detector. The near-perfect metrics from Pass #5 (PR-AUC 1.0) are explicitly demonstrated to be a temporal sampling artifact (`hour_cos`).

## Option 3 Rebuild
Per explicit instruction (Option 3), the pipeline has been rebuilt from specifications to match the Pass #5 constraints (148 malicious, 4229 benign observations) and simulate the temporal shortcut for rigorous evaluation.

## Limitations
Not yet completed: cross-dataset validation against CERT r6.2 (WAF/auth-gated download constraints).

## New Artifacts (10+ generated)
- Tables: `ablation_study.csv`, `model_evaluations.csv`, `significance_tests.csv`, `adversarial_diagnostics.csv`, `sampling_period_counts.csv`, `sampling_temporal_overlap.csv`, `feature_operationalization.csv`
- Figures: `temporal_distribution.png`, `hour_cos_distribution.png`, `day_of_week_distribution.png`

## Reproducibility Check
The pipeline was run twice with `random_state=42`. Diffing the outputs resulted in no differences (empty diff), proving determinism.
