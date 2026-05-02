# Heart & Mind: Predicting 5-Year Cardiovascular Risk in Young Adults (20–39) with Co-morbid Mental Disorders

This repository contains the machine learning pipeline for analyzing the intersection of cardiovascular risk and mental health burden in young adults, using the CDC National Health Interview Survey (NHIS) dataset.

## Research Objective
The project builds a binary classifier (High Risk vs. Low Risk) of Major Adverse Cardiac Events (MACE) using historical data, incorporating psychiatric comorbidity features alongside traditional cardiovascular risk factors.

## Dataset
Primary Data Source: [CDC National Health Interview Survey (NHIS)](https://www.cdc.gov/nchs/nhis/data-questionnaires-documentation.htm) 2022.

The data used in this study is public, de-identified survey data provided by the CDC.
**Ethical constraints strictly followed:** No protected health information (PHI) is stored or processed. The dataset is fully de-identified per CDC regulations. A demographic parity check is run during evaluation to flag biased predictions across sex/race subgroups.

## Requirements
Python 3.10+
See \`requirements.txt\` for package dependencies.

## Usage
1. Setup virtual environment and install requirements:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

2. Execute the full end-to-end pipeline:
   \`\`\`bash
   PYTHONPATH=src python src/pipeline.py --data_path data/nhis_raw/ --output_dir outputs/
   \`\`\`

## Outputs
- **Models:** \`outputs/models/\` (Random Forest, XGBoost)
- **Figures:** \`outputs/figures/\` (ROC curves, SHAP feature importance, Beeswarm, Dependence plot)
- **Logs:** \`outputs/experiment_log.csv\`
- **Architecture Diagram:** \`SYSTEM ARCHITECTURE.PNG\`

## Variables Used
- **Age:** AGEP_A (Filtered 20-39)
- **Mental health:** ANXEV_A (Anxiety), DEPEV_A (Depression), RX12M_A (Prescription Meds Proxy)
- **Cardiac (Target):** CHDEV_A, MIEV_A
- **Vitals:** BMICAT_A, HYPEV_A, DIBEV_A
- **Behavioral:** SMKNOW_A, DRKSTAT_A, WLKLEIS_A
- **Socioeconomic:** POVRATTC_A, EDUCP_A, SEX_A, HISPALLP_A
