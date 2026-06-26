import shap
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from preprocess import get_train_test_data

def explain_rf(X_train, X_test, model_path, output_dir):
    rf = joblib.load(model_path)
    explainer = shap.TreeExplainer(rf)

    # Take a sample for performance if dataset is large, but here it's small enough
    shap_values = explainer.shap_values(X_test)

    # For binary classification, shap_values is a list of arrays [class_0, class_1] in older SHAP versions
    # or just an array. We want explanations for the positive class (Infected = 1).
    if isinstance(shap_values, list):
        shap_vals_positive = shap_values[1]
    else:
        # In newer SHAP versions with sklearn RF, shap_values might be 3D (samples, features, classes)
        if len(shap_values.shape) == 3:
            shap_vals_positive = shap_values[:, :, 1]
        else:
            shap_vals_positive = shap_values

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_vals_positive, X_test, show=False)
    plt.savefig(os.path.join(output_dir, 'shap_summary_beeswarm.png'), bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_vals_positive, X_test, plot_type="bar", show=False)
    plt.savefig(os.path.join(output_dir, 'shap_summary_bar.png'), bbox_inches='tight')
    plt.close()

    # Calculate and print top 5 features
    mean_abs_shap = np.abs(shap_vals_positive).mean(axis=0)
    feature_importance = pd.DataFrame({
        'feature': X_test.columns,
        'importance': mean_abs_shap
    }).sort_values('importance', ascending=False)

    print("\n--- Top 5 Most Influential Features (SHAP Mean Absolute Value) ---")
    for i, row in feature_importance.head(5).iterrows():
        print(f"{i+1}. {row['feature']}: {row['importance']:.4f}")
        # Note: True interpretation depends on actual coefficients or beeswarm direction
        print(f"   Interpretation: Changes in {row['feature']} strongly impact the model's predicted risk score.\n")

    return explainer, shap_vals_positive

def explain_lr(X_train, X_test, model_path, output_dir):
    lr = joblib.load(model_path)
    # SHAP LinearExplainer requires data for background
    explainer = shap.LinearExplainer(lr, X_train, feature_perturbation="correlation_dependent")
    shap_values = explainer.shap_values(X_test)

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, show=False)
    plt.savefig(os.path.join(output_dir, 'shap_summary_beeswarm_lr.png'), bbox_inches='tight')
    plt.close()

def main():
    X_train, X_test, y_train, y_test = get_train_test_data()

    models_dir = 'outputs/models'
    figures_dir = 'outputs/figures'

    # Explain RF
    rf_path = os.path.join(models_dir, 'random_forest.pkl')
    explainer, shap_vals = explain_rf(X_train, X_test, rf_path, figures_dir)

    # Generate 3 individual force plots for high risk profiles
    rf = joblib.load(rf_path)
    probs = rf.predict_proba(X_test)[:, 1]
    high_risk_indices = np.argsort(probs)[-3:]

    # Use additive explainer for force plots or specifically grab the expected value
    if isinstance(explainer.expected_value, (list, np.ndarray)):
        ev = explainer.expected_value[1]
    else:
        ev = explainer.expected_value

    for i, idx in enumerate(high_risk_indices):
        plt.figure(figsize=(20, 5))
        # shap.force_plot requires JS for interactive, so we save static HTML or plot with matplotlib if possible
        # We will use shap.plots.waterfall for static individual plots as force_plot is interactive HTML by default

        # We need an Explanation object for waterfall
        exp = shap.Explanation(values=shap_vals[idx],
                               base_values=ev,
                               data=X_test.iloc[idx].values,
                               feature_names=X_test.columns.tolist())

        shap.plots.waterfall(exp, show=False)
        plt.savefig(os.path.join(figures_dir, f'shap_force_plot_high_risk_{i+1}.png'), bbox_inches='tight')
        plt.close()

    # Explain LR (just to have it as well for interpretability baseline)
    lr_path = os.path.join(models_dir, 'logistic_regression.pkl')
    explain_lr(X_train, X_test, lr_path, figures_dir)

if __name__ == '__main__':
    main()
