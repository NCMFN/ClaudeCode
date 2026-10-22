# Enterprise Digital Sanitization Detection Pipeline (Pass #6)

## Overview
This repository contains the evaluation pipeline for the detection of enterprise digital sanitization activity using authentication telemetry.

**Key Finding:** The near-perfect detection metrics reported in earlier iterations (PR-AUC 1.0) were primarily driven by a temporal shortcut. This Pass #6 revision repositions the contribution as a methodological framework for detecting temporal leakage and evaluating generalization in explainable insider-threat detection.

## Data Sources
- **LANL Comprehensive Cyber-Security Events:** Used for evaluating authentication behaviors tied to red team activities.
- **CERT Insider Threat Test Dataset (r6.2):** *Not yet completed: cross-dataset validation against CERT r6.2 remains infeasible due to download gating as previously documented.*

## Execution
Run the full pipeline using `python3 src/run_pipeline.py`.
