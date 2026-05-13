import os
import pandas as pd
import numpy as np

def test_directories_exist():
    assert os.path.exists("data/raw")
    assert os.path.exists("data/processed")
    assert os.path.exists("models")
    assert os.path.exists("results/figures")
    assert os.path.exists("results/metrics")
    assert os.path.exists("results/logs")

def test_metrics_exist():
    assert os.path.exists("results/metrics/all_results.csv")
    df = pd.read_csv("results/metrics/all_results.csv")
    assert len(df) > 0
    assert "F1" in df.columns
    assert "Latency_ms" in df.columns

def test_figures_exist():
    assert os.path.exists("results/figures/f1_scores_comparison.png")
    assert os.path.exists("results/figures/roc_auc_comparison.png")
    assert os.path.exists("results/figures/confusion_matrix_NSL-KDD_CNN_BiLSTM_Attn.png")
    assert os.path.exists("results/figures/pr_curve_NSL-KDD_CNN_BiLSTM_Attn.png")
    assert os.path.exists("results/figures/training_loss_curve_NSL-KDD.png")

def test_report_exists():
    assert os.path.exists("results/final_report.md")
    with open("results/final_report.md", "r") as f:
        content = f.read()
        assert "CNN-BiLSTM-Attn" in content
        assert "Isolation Forest" in content

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", "test_pipeline.py"])
