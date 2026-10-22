# Response to Reviewers

We thank the reviewers for their constructive feedback and overall positive assessment of the methodology. As recommended by Reviewer 4, this revision focuses on improving the framing, evidence, and rigor of the study. We have explicitly designated the work as a proxy feasibility study, added a SOTA comparison table, refined the statistical significance reporting, and augmented the feature importance analysis with directional explainability (SHAP). We have additionally addressed Reviewer 1 and 2's concerns regarding temporal validation and model explainability.

## Reviewer 4 Concerns

1. **Proxy Study Framing (also raised by R1, R2)**
   - **Action Taken:** We have explicitly reframed the paper as a proxy study. The title now includes "A Proxy Feasibility Study...". The abstract and Section headers have been updated to reflect the proxy nature of the dataset. The limitation regarding the proxy mapping has been front-loaded in the Executive Summary.
   - **Location:** Title, Executive Summary, Section Headers (`report/final_report.md`).

2. **Quantitative SOTA Comparison (also raised by R1)**
   - **Action Taken:** We added Table V, comparing our Random Forest and AdaBoost results with prior benchmarks on the AI4I dataset (Bezerra et al. and Besha et al.). We explicitly clarify that the difference in precision is a deliberate design choice (optimizing for recall/FNR under imbalance) rather than a model weakness.
   - **Location:** Table V in "Model Comparison Results on the AI4I Proxy Benchmark" (`report/final_report.md`).

3. **Wilcoxon Significance Framing and Bootstrap CI**
   - **Action Taken:** We reworded the statistical significance section to state the mathematical floor ($p=0.0625$ for $n=5$ paired folds) *before* reporting the p-value. Furthermore, we implemented a 95% bootstrap confidence interval on the ROC-AUC differences to provide a more informative uncertainty estimate.
   - **Location:** "Statistical Significance (ROC-AUC)" (`report/final_report.md`), `evaluate.py`, `report/bootstrap_auc_ci.csv`.

4. **Hedging Feature Importance and Adding Directional Explainability (also raised by R1)**
   - **Action Taken:** We added SHAP (TreeExplainer) to provide directional insights alongside the existing impurity-based importance. The caveat regarding impurity-based importance favoring continuous variables has been moved earlier in the text. Actionable guidance is now explicitly tied to the SHAP-confirmed direction of effect.
   - **Location:** "Feature Importance & Actionable Maintenance Guidance" (`report/final_report.md`), `evaluate.py`, `report/figures/shap_summary.png`.

5. **Author Name Order/Spelling Reconciliation**
   - **Action Taken:** We acknowledge the discrepancy between the submission metadata and the PDF byline.
   - **Note to Chairs:** We will ensure the submission system metadata perfectly matches the preferred canonical order in the PDF byline prior to the camera-ready deadline.

## Additional Concerns

1. **Lack of Time-Based Validation (R1, R2)**
   - **Action Taken:** We have added a paragraph to the Limitations section explicitly stating that genuine temporal or multi-site validation is not possible due to the lack of timestamps/site IDs in the proxy dataset. We also detail what such validation would entail given real-world data.
   - **Location:** "Limitations" (`report/final_report.md`).
