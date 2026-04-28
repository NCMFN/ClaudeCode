# Digital Sanitization Detection Pipeline

## 1. Data Acquisition & Storage Layer
- Simulated Sources (e.g., CCFD)
- Future Real-World Sources (e.g., CERT, LANL)
- Raw Log Storage (Data Lake)

## 2. Preprocessing & Feature Engineering Layer
- Log Parser & Normalizer (Cleaning, Formatting)
- Feature Extraction Engine (Domain specific indicators)
- Feature Store (Vectorized Data)

## 3. Experimental Design & Splitting Layer
- Strict Data Splitter
- 80% Data: Training/Validation Sets
- 20% Data (Untouched): Held-Out Test Set (Real Imbalance)

## 4. Model Development & Training Layer
- Resampling Engine (SMOTE, Undersampling)
- Balanced/Augmented Data
- Model Training Engine
- Support Vector Machine (SVM) [Champion Model]

## 5. Evaluation & Robustness Layer
- Cross-Validation Evaluator (On Resampled Data)
- Overestimated Metrics (e.g., High ROC-AUC)
- Realistic Evaluator (On Held-Out Imbalanced Data) [Critical Realistic Evaluation Path]
- Deployable Metrics (PR-AUC, Recall)
- Adversarial Simulator (Feature Suppression Attacks)

## 6. Reporting & Output Layer
- CV Performance Report
- Held-Out Performance Report
- Comparison Dashboard (Highlighting Evaluation Gaps)
- Final Detection Alerts

## Legend
- Green Box = Champion Model
- Red Outline/Pink Box = Critical Realistic Evaluation Path
