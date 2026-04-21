import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_loader import load_and_audit_data
from src.feature_engineering import engineer_features
from src.preprocessing import preprocess_and_split
from src.models import train_xgboost, train_isolation_forest
from src.evaluation import train_baselines_and_evaluate, plot_evaluation
from src.shap_analysis import run_shap_analysis
from src.trust_score import compute_and_save_trust_scores

def create_summary_report(output_path, df_orig_shape, num_features, pre_smote_counts, post_smote_counts, metrics_df, top_shap_features):
    print("Generating Final Summary Report...")
    lines = []
    lines.append("=== IEEE Paper Reproduction: Solana Rug Pull Detection ===\n\n")

    lines.append("--- Dataset Statistics ---\n")
    lines.append(f"Original Rows: {df_orig_shape[0]}, Columns: {df_orig_shape[1]}\n")
    lines.append(f"Engineered Features: {num_features}\n")
    lines.append(f"Class Balance (Pre-SMOTE Train Set):\n{pre_smote_counts}\n")
    lines.append(f"Class Balance (Post-SMOTE Train Set):\n{post_smote_counts}\n\n")

    lines.append("--- Model Evaluation Metrics ---\n")
    lines.append(metrics_df.to_string(index=False) + "\n\n")

    lines.append("--- Top 5 Features (SHAP Importance) ---\n")
    for i, f in enumerate(top_shap_features):
        lines.append(f"{i+1}. {f}\n")
    lines.append("\n")

    lines.append("--- Notes on Limitations vs Paper ---\n")
    lines.append("The paper describes 23 total features. SolRPDS provides raw transaction and liquidity logs. ")
    lines.append("Smart contract authority flags (e.g., mint authority, freeze authority) and social media ")
    lines.append("metadata could not be derived exclusively from SolRPDS. Extracting these would require ")
    lines.append("direct Solana RPC API integration or secondary datasets. The engineered features here ")
    lines.append("represent the maximum expressible proxy features from the given data.\n\n")

    lines.append("--- Target Metrics Comparison ---\n")
    xgb_row = metrics_df[metrics_df['Model'] == 'XGBoost'].iloc[0]
    lines.append(f"XGBoost Test F1: {xgb_row['F1-Score']:.4f} (Paper Target: 0.904)\n")
    lines.append(f"XGBoost Test AUC-ROC: {xgb_row['AUC-ROC']:.4f} (Paper Target: 0.941)\n")

    with open(output_path, "w") as f:
        f.writelines(lines)
    print(f"Summary report saved to {output_path}")

def plot_class_distribution(pre_smote, post_smote, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.barplot(x=pre_smote.index, y=pre_smote.values, ax=axes[0], palette="viridis")
    axes[0].set_title('Class Distribution (Before SMOTE)')
    axes[0].set_xlabel('Class (0=Legit, 1=Rug)')
    axes[0].set_ylabel('Count')

    sns.barplot(x=post_smote.index, y=post_smote.values, ax=axes[1], palette="viridis")
    axes[1].set_title('Class Distribution (After SMOTE)')
    axes[1].set_xlabel('Class (0=Legit, 1=Rug)')
    axes[1].set_ylabel('Count')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def generate_manifest(base_dir):
    outputs_dir = os.path.join(base_dir, "outputs")
    manifest_path = os.path.join(outputs_dir, "manifest.txt")
    print("Generating manifest...")

    descriptions = {
        "data_loader/data_audit.txt": "Data audit report including shapes, duplicates, and missing values.",
        "feature_engineering/features_engineered.csv": "Engineered feature dataset ready for modeling.",
        "main/class_distribution.png": "Plot of class distribution before and after SMOTE oversampling.",
        "models/xgboost_best_model.pkl": "Serialized XGBoost model optimized via GridSearchCV.",
        "evaluation/model_comparison_table.csv": "Table of test set evaluation metrics for XGBoost, Random Forest, Logistic Regression, and Isolation Forest.",
        "evaluation/roc_curve_comparison.png": "ROC curves overlaying all trained models.",
        "evaluation/precision_recall_curve.png": "Precision-Recall curves for XGBoost and Random Forest.",
        "evaluation/confusion_matrix_xgb.png": "Confusion matrix heatmap for the XGBoost model predictions.",
        "evaluation/feature_importance_xgb.png": "Bar plot of top 15 features ranked by XGBoost gain importance.",
        "shap_analysis/shap_summary_bar.png": "Bar plot of mean absolute SHAP values for top features.",
        "shap_analysis/shap_summary_beeswarm.png": "Beeswarm plot of SHAP values illustrating directional impact.",
        "shap_analysis/shap_waterfall_sample.png": "Waterfall SHAP explanation plot for a single high-confidence prediction.",
        "trust_score/test_trust_scores.csv": "Computed Trust Scores and risk tiers alongside probabilities for the test set.",
        "trust_score/trust_score_distribution.png": "Histogram of the Trust Score distribution stratified by the true label.",
        "main/experiment_summary.txt": "Final summary text report including dataset stats, top features, and metrics compared against paper baselines."
    }

    manifest_lines = ["=== Output Manifest ===\n\n"]
    for root, dirs, files in os.walk(outputs_dir):
        if "manifest.txt" in files:
            continue
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, outputs_dir)
            size_kb = os.path.getsize(full_path) / 1024.0

            # Map description by relative path, default if not exact match
            desc = descriptions.get(rel_path, "Generated output file.")
            manifest_lines.append(f"File: {rel_path}\nSize: {size_kb:.2f} KB\nDescription: {desc}\n\n")

    with open(manifest_path, "w") as f:
        f.writelines(manifest_lines)
    print(f"Manifest saved to {manifest_path}")

def main():
    start_time = time.time()
    print("=== Pipeline Started ===")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    outputs_dir = os.path.join(base_dir, "outputs")

    # Define tool-specific output directories
    dl_dir = os.path.join(outputs_dir, "data_loader")
    fe_dir = os.path.join(outputs_dir, "feature_engineering")
    main_dir = os.path.join(outputs_dir, "main")
    models_dir = os.path.join(outputs_dir, "models")
    eval_dir = os.path.join(outputs_dir, "evaluation")
    shap_dir = os.path.join(outputs_dir, "shap_analysis")
    ts_dir = os.path.join(outputs_dir, "trust_score")

    # Create all directories
    for d in [dl_dir, fe_dir, main_dir, models_dir, eval_dir, shap_dir, ts_dir]:
        os.makedirs(d, exist_ok=True)

    df_raw = load_and_audit_data(data_dir, os.path.join(dl_dir, "data_audit.txt"))
    orig_shape = df_raw.shape

    features_csv = os.path.join(fe_dir, "features_engineered.csv")
    df_features = engineer_features(df_raw, features_csv)

    (X_train, y_train), (X_train_sm, y_train_sm), (X_val, y_val), (X_test, y_test), continuous_cols = preprocess_and_split(df_features, max_samples_per_class=5000)

    plot_class_distribution(
        y_train.value_counts(),
        y_train_sm.value_counts(),
        os.path.join(main_dir, "class_distribution.png")
    )

    xgb_model_path = os.path.join(models_dir, "xgboost_best_model.pkl")
    best_xgb, xgb_metrics = train_xgboost(X_train_sm, y_train_sm, X_test, y_test, xgb_model_path)

    if_model, if_metrics, _ = train_isolation_forest(X_train, X_test, y_test)

    comp_csv = os.path.join(eval_dir, "model_comparison_table.csv")
    models, df_res = train_baselines_and_evaluate(
        X_train, y_train, X_train_sm, y_train_sm, X_test, y_test, best_xgb, if_model, comp_csv
    )
    plot_evaluation(models, if_model, X_test, y_test, eval_dir)

    top_shap_features = run_shap_analysis(best_xgb, X_test, shap_dir)

    ts_csv = os.path.join(ts_dir, "test_trust_scores.csv")
    compute_and_save_trust_scores(best_xgb, X_test, y_test, ts_csv, ts_dir)

    summary_txt = os.path.join(main_dir, "experiment_summary.txt")
    create_summary_report(
        summary_txt,
        orig_shape,
        X_train.shape[1],
        y_train.value_counts(),
        y_train_sm.value_counts(),
        df_res,
        top_shap_features[:5]
    )

    generate_manifest(base_dir)

    print(f"=== Pipeline Completed in {time.time() - start_time:.2f} seconds ===")

if __name__ == "__main__":
    main()
