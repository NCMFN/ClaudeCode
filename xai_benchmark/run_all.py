import os
import sys
import argparse

# Add current dir to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessing.data_loader import load_all_datasets, preprocess_dataset
from models.train import train_model, evaluate_model, evaluate_cv
from explainers.explainers import SHAPExplainer, LIMEExplainer
from metrics.metrics import (
    calculate_fidelity, calculate_stability, calculate_simplicity,
    calculate_relevance, calculate_q_score
)
from evaluation.evaluator import run_experiment_loop, run_statistical_tests, run_ablation_study
from visualizations.plotter import (
    plot_confusion_matrix, plot_roc_curve, plot_pr_curve, plot_learning_curve,
    plot_shap_summary, plot_lime_bar, plot_metric_comparisons, plot_ablation_study
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Run XAI Benchmark")
    parser.add_argument('--fast', action='store_true', help="Run in fast mode (downsamples large datasets, caps explainers)")
    args = parser.parse_args()

    print(f"Starting XAI Benchmark Pipeline... (Fast mode: {args.fast})")

    # 1. Load Data
    datasets_dict = load_all_datasets(fast_mode=args.fast)

    # Define explainer capping
    MAX_EXPLAIN_SAMPLES = 50 if args.fast else None # Significantly reduce to speed up tests

    # 2. Preliminary Model Evaluation (Seed 42) & Visualizations
    model_performance_records = []

    print("\n================ Generating Baseline Models & Plots ================")
    for dataset_name, df in datasets_dict.items():
        data_dict = preprocess_dataset(df.copy(), dataset_name)
        X_train = data_dict['X_train']
        X_test = data_dict['X_test']
        y_train = data_dict['y_train']
        y_test = data_dict['y_test']
        feature_names = data_dict['feature_names']

        # Train
        model = train_model(X_train, y_train, seed=42)

        # Evaluate & Log
        metrics, y_pred, y_proba = evaluate_model(model, X_test, y_test, dataset_name)
        metrics['Dataset'] = dataset_name
        model_performance_records.append(metrics)

        # Visualizations
        plot_confusion_matrix(y_test, y_pred, dataset_name)
        plot_roc_curve(y_test, y_proba, dataset_name)
        plot_pr_curve(y_test, y_proba, dataset_name)

        # XAI Global Plots
        # Cap samples if fast mode is enabled
        X_test_explain = X_test[:MAX_EXPLAIN_SAMPLES] if MAX_EXPLAIN_SAMPLES and len(X_test) > MAX_EXPLAIN_SAMPLES else X_test
        y_test_explain = y_test[:MAX_EXPLAIN_SAMPLES] if MAX_EXPLAIN_SAMPLES and len(y_test) > MAX_EXPLAIN_SAMPLES else y_test

        shap_explainer = SHAPExplainer(model)
        shap_vals = shap_explainer.explain(X_test_explain)
        plot_shap_summary(shap_vals, X_test_explain, feature_names, dataset_name)

        lime_explainer = LIMEExplainer(X_train, feature_names)
        lime_vals = lime_explainer.explain(model, X_test_explain)
        plot_lime_bar(lime_vals, feature_names, dataset_name)

    # Save model performance
    import pandas as pd
    pd.DataFrame(model_performance_records).to_csv(os.path.join(RESULTS_DIR, 'model_performance.csv'), index=False)

    # 3. Main Experimental Loop (across seeds)
    explainer_fns = {
        'shap': SHAPExplainer,
        'lime': LIMEExplainer
    }

    metric_fns = {
        'fidelity': calculate_fidelity,
        'stability': calculate_stability,
        'simplicity': calculate_simplicity,
        'relevance': calculate_relevance,
        'q_score': calculate_q_score
    }

    # Redefine preprocess_dataset wrapper to pass seed and cap test set size if fast mode
    def preprocess_wrapper(df, name, seed):
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        import numpy as np

        if df.isnull().sum().sum() > 0:
            for col in df.columns:
                if df[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(df[col].median())
                    else:
                        df[col] = df[col].fillna(df[col].mode()[0])

        non_numeric = df.select_dtypes(exclude=[np.number]).columns
        if len(non_numeric) > 0:
            df = pd.get_dummies(df, columns=non_numeric, drop_first=True)

        y = df['target'].values
        X = df.drop(columns=['target'])
        feature_names = X.columns.tolist()
        X = X.values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, stratify=y, random_state=seed
        )

        # In the main loop, if fast mode is enabled, cap the test set size so that
        # metric calculations (which run explainers on all X_test) are faster.
        if args.fast and MAX_EXPLAIN_SAMPLES and len(X_test) > MAX_EXPLAIN_SAMPLES:
            X_test = X_test[:MAX_EXPLAIN_SAMPLES]
            y_test = y_test[:MAX_EXPLAIN_SAMPLES]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'X_train_unscaled': X_train,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': feature_names
        }

    results_df = run_experiment_loop(datasets_dict, preprocess_wrapper, train_model, explainer_fns, metric_fns)
    results_df.to_csv(os.path.join(RESULTS_DIR, 'all_metrics_results.csv'), index=False)

    # 4. Statistical Tests
    stats_df = run_statistical_tests(results_df)
    stats_df.to_csv(os.path.join(RESULTS_DIR, 'statistical_tests.csv'), index=False)

    # 5. Ablation Study
    ablation_df = run_ablation_study(results_df)
    ablation_df.to_csv(os.path.join(RESULTS_DIR, 'ablation_study.csv'), index=False)

    # 6. Final Visualizations
    plot_metric_comparisons(results_df)
    plot_ablation_study(ablation_df)

    print("\nPipeline completed successfully! Results saved to /results and /visualizations.")

if __name__ == "__main__":
    main()
