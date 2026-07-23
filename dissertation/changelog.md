# Dissertation Merge Changelog

## Phase 1: Architecture
- Created standard PhD thesis directory structure using `report` class.
- Written new Chapter 1 (Introduction) to unify the problem statement around evaluation artifacts in rare-event digital sanitization detection.

## Phase 2: Content Transplantation & Synthesis
- **Literature Review (Chapter 2)**: Merged Study A and Study B's reviews thematically. Removed Study B's `\thebibliography` environment and converted all citations to BibTeX format.
- **Methodology (Chapter 3)**: Created a unified introductory section linking both studies' methodologies, followed by the specific experimental setups for Study A and Study B.
- **Results (Chapters 4 & 5)**: Transplanted the results sections verbatim from Study A and Study B, ensuring the critical negative results (SMOTE-CV optimism and temporal leakage) were fully preserved.
- **Synthesis & Conclusion (Chapters 6 & 7)**: Authored original synthesis prose exploring the cross-study implications of evaluation leakage and the differing actionability of SHAP/LIME in forensic versus telemetry spaces.

## Phase 3: Consistency & Normalization
- Converted Study B's inline `\bibitem` entries into BibTeX and merged them with Study A's `refs.bib`, deduplicating entries.
- Re-routed all figure and table inputs to a unified `assets/` directory to simplify the LaTeX project structure.
- Removed IEEE-specific front matter (e.g., `\IEEEauthorblock`, `\IEEEkeywords`) from the transplanted chapters to fit the `report` class.

## Phase 4: Artifact Preservation
- Included a zipped archive of Study B's computational pipeline (`studyB_pipeline_code.tar.gz`) in the `assets/` directory for reproducibility.
