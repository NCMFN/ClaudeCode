# Cross-domain XAI Benchmarks

This repository implements the research paper "Cross-domain XAI Benchmarks: Developing Unified Evaluation Suites that Assess Explanation Quality Across Healthcare and Finance Domains."

It evaluates SHAP and LIME across 6 datasets (3 Healthcare, 3 Finance) using a Four-Metric Framework (Fidelity, Stability, Simplicity, Relevance) and produces an aggregated Q-Score.

## Project Structure

```
xai_benchmark/
├── data/               # Raw datasets (downloaded automatically)
├── preprocessing/      # Data loading & preprocessing scripts
├── models/             # Random Forest training and evaluation
├── explainers/         # SHAP and LIME explanation generation
├── metrics/            # Fidelity, Stability, Simplicity, Relevance implementations
├── evaluation/         # Aggregate scoring, statistical tests, ablation study
├── visualizations/     # All plots and figures output directory
├── results/            # CSV/JSON output of all results
├── tests/              # Unit tests for custom metrics
├── run_all.py          # Main execution script
└── requirements.txt    # Required dependencies
```

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the end-to-end pipeline:
   ```bash
   python run_all.py
   ```

   To run in fast mode (downsamples large datasets like Credit Card Fraud and limits explainers):
   ```bash
   python run_all.py --fast
   ```

   The `run_all.py` script automatically downloads the required datasets. If datasets fail to download (e.g., Kagglehub rate limits), the script implements a graceful fallback and processes available datasets.
   *Note: Deep Learning based explainers like Integrated Gradients and Grad-CAM require differentiable models and are reserved for future work.*

## Datasets
* **Healthcare**: Breast Cancer Wisconsin, Heart Disease (UCI), Pima Indians Diabetes
* **Finance**: Credit Card Fraud, Loan Default, Financial Distress

## Table I: Comparison of XAI Evaluation Frameworks

| Framework | Main Focus | Cross-Domain | Validation | Metrics Used | Reproducible |
|-----------|------------|--------------|------------|--------------|--------------|
| EvaluateXAI | NLP/Vision | No | Human + Proxy | Fidelity, Plausibility | Partial |
| Deters et al. | Clinical | No | Proxy | Stability, Consistency | Yes |
| Sokol & Flach | Tabular | No | Theoretical | Actionability | No |
| RexQUAL | Finance | No | Proxy | Fidelity, Sparsity | Yes |
| Perotti et al. | Healthcare | No | Proxy | Fidelity, Accuracy | Yes |
| **Proposed Framework** | **Healthcare/Finance** | **Yes** | **Proxy (4 metrics)** | **Fidelity, Stability, Simplicity, Relevance** | **Yes** |

## Outputs
- `results/all_metrics_results.csv`: Metric scores per method/dataset/seed
- `results/statistical_tests.csv`: Paired t-tests, Cohen's d, CI
- `results/ablation_study.csv`: Results of removing metrics
- `results/model_performance.csv`: Accuracy, F1, PR-AUC per dataset
- `visualizations/`: ROC/PR curves, confusion matrices, SHAP/LIME global plots, metric comparisons
