import shap
import matplotlib.pyplot as plt
import os
import numpy as np
import xgboost

def run_shap_analysis(model, X_test, output_dir: str):
    print("Running SHAP Analysis...")
    os.makedirs(output_dir, exist_ok=True)

    booster = model.get_booster()
    try:
        config = booster.save_config()
        config = config.replace('"[5E-1]"', '"0.5"')
        booster.load_config(config)
        explainer = shap.TreeExplainer(booster)
        shap_values = explainer.shap_values(X_test)
    except Exception as e:
        print(f"Fallback to Native XGBoost SHAP calculation due to: {e}")
        shap_values_raw = booster.predict(xgboost.DMatrix(X_test), pred_contribs=True)
        shap_values = shap_values_raw[:, :-1]
        expected_value = shap_values_raw[0, -1]

        class MockExplainer:
            def __init__(self, ev):
                self.expected_value = ev
        explainer = MockExplainer(expected_value)

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
    plt.title('SHAP Mean Absolute Importance')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_summary_bar.png'), dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, show=False)
    plt.title('SHAP Summary (Beeswarm)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_summary_beeswarm.png'), dpi=300, bbox_inches='tight')
    plt.close()

    y_proba = model.predict_proba(X_test)[:, 1]
    high_conf_idx = np.argmax(y_proba)

    base_val = explainer.expected_value
    if isinstance(base_val, list) or isinstance(base_val, np.ndarray):
        base_val = base_val[1] if len(base_val) > 1 else base_val[0]

    exp = shap.Explanation(
        values=shap_values[high_conf_idx],
        base_values=base_val,
        data=X_test.iloc[high_conf_idx],
        feature_names=X_test.columns
    )

    plt.figure(figsize=(10, 8))
    shap.plots.waterfall(exp, show=False)
    plt.title(f'SHAP Waterfall for Sample {high_conf_idx} (Prob: {y_proba[high_conf_idx]:.3f})')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'shap_waterfall_sample.png'), dpi=300, bbox_inches='tight')
    plt.close()

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    top_indices = np.argsort(mean_abs_shap)[::-1][:5]
    top_features = X_test.columns[top_indices]

    print("\nTop 5 Important Features (by mean |SHAP|):")
    for i, feature in enumerate(top_features):
        print(f"{i+1}. {feature} (score: {mean_abs_shap[top_indices[i]]:.4f})")

    return top_features
