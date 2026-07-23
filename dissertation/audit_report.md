# Phase 0: Audit Report

## Inventory

### Study A: "MDS"
- **Files:** `bare_jrnl.tex`, `refs.bib`
- **Sections:** Introduction, Literature Review, Methodology (Research Design, Dataset Description, Preprocessing, Feature Engineering, Data Partitioning and Class Balancing, Model Training and Cross Validation, Evaluation Metrics), Results & Discussion (Cross-Validation Performance on SMOTE-Balanced Data, Test Set Performance on Imbalanced Data, Impact of Class Imbalance on Model Behaviour, Robustness Under Anti-Forensic Feature Suppression, Explainability Results, Discussion, Summary), Conclusion (Limitations and Future Work)
- **Figures:** 6 `\begin{figure}` environments (files provided: DSD2-16, system_architecture.png)
- **Tables:** 8 `\begin{table}` environments
- **Bibliography:** 68 entries in `refs.bib`.
- **Inconsistencies:** There are 12 un-cited bibliography entries in `refs.bib`: 'ref31', 'ref62', 'ref68', 'ref67', 'ref21', 'ref64', 'ref50', 'ref65', 'ref61', 'ref63', 'ref66', 'ref57'.

### Study B: "EAAD"
- **Files:** `main.tex`, `verified_update.tex`, `study_assets/`, `pass5_assets/`, `generated_tables/`
- **Sections:** Introduction, Literature Review (Evolution of Insider Threat Detection Research, Reconstruction and Behavioral Baselines, Relational and Graph-Based Modeling, Supervised Learning, Explainability, and Robustness, Imbalance Handling and Session Graphs, Explainable and Operational Frameworks, Summary of Related Works), Methodology (Dataset, Ground Truth, and Sampling, Feature Engineering, Models and Baselines, Evaluation Protocol and Leakage Control, Explainability and Reproducibility), Results (Held-Out Performance and Cross-Validation, Statistical Comparison, Feature Attribution and Ablation, Adversarial Robustness and Distribution Shift, Complexity and Deployability), Discussion (Interpretation of the Near-Perfect Scores, Methodological Implications, Scope Limitations, Operational Implications and Future Work), Conclusion
- **Figures:** 8 `\begin{figure}` environments
- **Tables:** 7 `\begin{table}` environments directly in tex (some `\input` from generated tables)
- **Bibliography:** 30 entries inline in `main.tex` (`\begin{thebibliography}`).
- **Inconsistencies:** No broken citation references. All `\cite`s resolve to a `\bibitem`.

## Merge Plan Note
- Study B's `\bibitem` entries will need to be converted to `.bib` format to be merged with Study A's `refs.bib`.
- Will use standard `report` class for the dissertation structure.
- "Digital sanitization" vs "anti-forensic" terminology will be normalized.
