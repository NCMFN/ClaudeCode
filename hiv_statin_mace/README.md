# Predicting Statin Benefit in HIV+ Populations

This repository contains the machine learning pipeline for the research paper:
**"Predicting Statin Benefit in HIV+ Populations: Optimizing Cardiovascular Risk Scores through Machine Learning Efficacy Analysis of Pitavastatin Calcium."**

## Objective
Build a binary classification model that predicts which HIV-positive patients (classified as "low-to-moderate" risk by traditional scores) will experience a Major Adverse Cardiac Event (MACE) without statin intervention, benchmarking against Framingham and ASCVD risk scores.

## Data Access Instructions
### Primary Dataset: REPRIEVE Trial
The primary data source for this model is the REPRIEVE (Randomized Trial to Prevent Vascular Events in HIV) clinical trial.
To request access to the true clinical dataset:
1. Visit the NHLBI Biologic Specimen and Data Repository Information Coordinating Center (BioLINCC)
2. Navigate to: [REPRIEVE Study Page](https://biolincc.nhlbi.nih.gov/studies/reprieve/)
3. Follow the data request procedures.

### Fallback Dataset: NA-ACCORD
If REPRIEVE data is unavailable, NA-ACCORD cohort data can be requested:
[NA-ACCORD Data Requests](https://naaccord.org/data-requests)

### Synthetic Data Disclaimer
**WARNING:** If the code is run without providing real data, it will automatically generate a **synthetic dataset** (`synthetic.py`) based on published REPRIEVE summary statistics (Bhatt DL et al., NEJM 2023) for development and testing purposes.

This synthetic dataset is NOT real patient data and results obtained using it do not represent true clinical findings. All outputs generated using this synthetic dataset will be flagged.

## Ethical Use Statement
This machine learning model and its associated code are strictly intended for **research purposes only**.
**It must NOT be used for clinical decision-making, patient diagnosis, or treatment planning** without prospective, peer-reviewed validation in an independent, real-world HIV cohort.

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Run data generation: `cd src && python synthetic.py`
3. Train models: `python train.py`
4. Evaluate and generate figures: `python evaluate.py`
