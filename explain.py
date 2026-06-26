import shap
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
import warnings

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def explain_model(model, X_test, output_dir='outputs'):
    """
    Generates SHAP plots to explain the model.
    """
    os.makedirs(output_dir, exist_ok=True)
    logging.info("Computing SHAP values...")

    # Supress lightgbm warnings during shap computation
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        explainer = shap.TreeExplainer(model)

        # Subsample for speed if dataset is too large, but 20% of 255k is ~50k.
        # SHAP on 50k can be slow. Sample 5000 for explainability.
        if len(X_test) > 5000:
            logging.info("Subsampling X_test for SHAP evaluation to 5000 samples for performance.")
            X_sample = X_test.sample(5000, random_state=42)
        else:
            X_sample = X_test

        shap_values = explainer(X_sample)

    # Check if lightgbm outputs log odds array with shap values (binary classification shape might be weird)
    # TreeExplainer for lightgbm binary classification usually returns (N, M) shap values for the log odds.
    if isinstance(shap_values, list) and len(shap_values) == 2:
         # Depending on LightGBM version, it might return a list [class0, class1]
         shap_values = shap_values[1]

    logging.info("Plotting global SHAP summary (beeswarm)...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, max_display=15, show=False)
    plt.title("SHAP Summary (Top 15 Features)")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_summary_beeswarm.png'))
    plt.close()

    logging.info("Plotting global SHAP bar chart...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_sample, plot_type="bar", max_display=15, show=False)
    plt.title("SHAP Feature Importance")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_summary_bar.png'))
    plt.close()

    # Identify top 5 most important features by mean |SHAP value|
    mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    top_indices = np.argsort(mean_abs_shap)[::-1][:5]
    top_features = X_sample.columns[top_indices]
    logging.info(f"Top 5 most important features: {list(top_features)}")

    # Find local instances
    # We need predictions to find highest confidence default, safe, and borderline
    y_pred_proba = model.predict_proba(X_sample)[:, 1]

    idx_default = np.argmax(y_pred_proba)
    idx_safe = np.argmin(y_pred_proba)
    idx_border = np.argmin(np.abs(y_pred_proba - 0.5))

    logging.info("Plotting local SHAP waterfall plots...")

    # 1. Highest-confidence default
    plt.figure(figsize=(10, 6))
    shap.waterfall_plot(shap_values[idx_default], show=False)
    plt.title(f"Highest-Confidence Default (Prob: {y_pred_proba[idx_default]:.2f})")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_waterfall_default.png'))
    plt.close()

    # 2. Highest-confidence safe
    plt.figure(figsize=(10, 6))
    shap.waterfall_plot(shap_values[idx_safe], show=False)
    plt.title(f"Highest-Confidence Safe (Prob: {y_pred_proba[idx_safe]:.2f})")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_waterfall_safe.png'))
    plt.close()

    # 3. Borderline case
    plt.figure(figsize=(10, 6))
    shap.waterfall_plot(shap_values[idx_border], show=False)
    plt.title(f"Borderline Prediction (Prob: {y_pred_proba[idx_border]:.2f})")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_waterfall_borderline.png'))
    plt.close()

    logging.info(f"SHAP plots saved to {output_dir}/")

if __name__ == "__main__":
    pass
