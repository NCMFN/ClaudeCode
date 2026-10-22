import yaml
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix, roc_curve, precision_recall_curve
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt
import seaborn as sns

from preprocessing import get_preprocessor, handle_imbalance
from models import get_models

def compute_cohens_d(x, y):
    diff = x - y
    return np.mean(diff) / (np.std(diff, ddof=1) + 1e-8)

def evaluate_models(X, y, config_path='config.yaml', run_id=1):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    random_seed = config.get('random_seed', 42)
    cv_folds = config.get('cv_folds', 5)
    imbalance_strategy = config.get('imbalance_strategy', 'smote')
    output_paths = config.get('output_paths', {})

    models = get_models(config_path)

    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_seed)

    metrics_summary = []
    roc_curves_data = {}
    pr_curves_data = {}
    confusion_matrices_data = {}
    fold_roc_aucs = {name: [] for name in models.keys()}

    best_model_name = None
    best_model_auc = -1
    best_model_fitted = None
    best_model_preprocessor = None
    best_X_test = None

    for model_name, model in models.items():
        print(f"Evaluating {model_name}...")

        fold_metrics = {
            'Accuracy': [], 'Precision': [], 'Recall': [], 'F1-score': [],
            'ROC-AUC': [], 'PR-AUC': [], 'False Negative Rate': []
        }

        all_y_test = []
        all_y_pred = []
        all_y_prob = []

        for train_idx, test_idx in skf.split(X, y):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            preprocessor = get_preprocessor()
            X_train_proc = preprocessor.fit_transform(X_train)
            X_test_proc = preprocessor.transform(X_test)

            # handle imbalance on train only
            X_train_res, y_train_res = handle_imbalance(X_train_proc, y_train, strategy=imbalance_strategy, random_seed=random_seed)

            model.fit(X_train_res, y_train_res)

            y_pred = model.predict(X_test_proc)
            y_prob = model.predict_proba(X_test_proc)[:, 1]

            all_y_test.extend(y_test)
            all_y_pred.extend(y_pred)
            all_y_prob.extend(y_prob)

            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            roc_auc = roc_auc_score(y_test, y_prob)
            pr_auc = average_precision_score(y_test, y_prob)

            tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
            fnr = fn / (fn + tp) if (fn + tp) > 0 else 0

            fold_metrics['Accuracy'].append(acc)
            fold_metrics['Precision'].append(prec)
            fold_metrics['Recall'].append(rec)
            fold_metrics['F1-score'].append(f1)
            fold_metrics['ROC-AUC'].append(roc_auc)
            fold_metrics['PR-AUC'].append(pr_auc)
            fold_metrics['False Negative Rate'].append(fnr)

            fold_roc_aucs[model_name].append(roc_auc)

        # Average metrics
        avg_metrics = {k: float(np.mean(v)) for k, v in fold_metrics.items()}
        avg_metrics['Model'] = model_name
        metrics_summary.append(avg_metrics)

        # Save curve data for the full concatenated OOF predictions
        fpr, tpr, _ = roc_curve(all_y_test, all_y_prob)
        roc_curves_data[model_name] = (fpr, tpr, np.mean(fold_metrics['ROC-AUC']))

        cm = confusion_matrix(all_y_test, all_y_pred, labels=[0, 1])
        confusion_matrices_data[model_name] = cm

        if avg_metrics['ROC-AUC'] > best_model_auc:
            best_model_auc = avg_metrics['ROC-AUC']
            best_model_name = model_name
            # Re-fit on full data for feature importance (or at least full last fold)
            # To be rigorous, fit on entire dataset
            best_model_fitted = model
            best_model_preprocessor = preprocessor

    # Significance testing (pairwise against the best model)
    significance_results = []
    best_aucs = np.array(fold_roc_aucs[best_model_name])
    for model_name in models.keys():
        if model_name != best_model_name:
            comp_aucs = np.array(fold_roc_aucs[model_name])
            if np.all(best_aucs == comp_aucs):
                p_val = 1.0
                d = 0.0
            else:
                stat, p_val = wilcoxon(best_aucs, comp_aucs, zero_method='zsplit')
                d = compute_cohens_d(best_aucs, comp_aucs)
            significance_results.append({
                'Comparison': f"{best_model_name} vs {model_name}",
                'p-value': float(p_val),
                'Cohen_d': float(d),
                'Significant (alpha=0.05)': bool(p_val < 0.05)
            })

    # Save artifacts
    df_metrics = pd.DataFrame(metrics_summary)
    df_metrics.to_csv(output_paths['metrics_summary'], index=False)

    df_sig = pd.DataFrame(significance_results)
    df_sig.to_csv(output_paths['significance_tests'], index=False)

    run_metrics_path = output_paths[f'run{run_id}_metrics']
    with open(run_metrics_path, 'w') as f:
        # Convert df_metrics to dict and save as json
        json.dump(df_metrics.to_dict(orient='records'), f, indent=4)

    # Plot ROC curves
    plt.figure(figsize=(8, 6))
    for model_name, (fpr, tpr, auc_val) in roc_curves_data.items():
        plt.plot(fpr, tpr, label=f"{model_name} (AUC = {auc_val:.3f})")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(output_paths['roc_curves'], dpi=300)
    plt.close()

    # Plot Confusion Matrices
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, (model_name, cm) in zip(axes, confusion_matrices_data.items()):
        cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', ax=ax)
        ax.set_title(f"{model_name} (Row-Normalized)")
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
    plt.tight_layout()
    plt.savefig(output_paths['confusion_matrices'], dpi=300)
    plt.close()

    # Feature Importance for the best model
    # Re-fit best model on full data for shap/feature importance
    X_proc = best_model_preprocessor.fit_transform(X)
    X_res, y_res = handle_imbalance(X_proc, y, strategy=imbalance_strategy, random_seed=random_seed)
    best_model_fitted.fit(X_res, y_res)

    # Get feature names from preprocessor
    num_cols = ['Air temperature', 'Process temperature', 'Rotational speed', 'Torque', 'Tool wear', 'Thermal_delta', 'Mechanical_power']
    cat_encoder = best_model_preprocessor.named_transformers_['cat']
    cat_cols = cat_encoder.get_feature_names_out(['Type']).tolist()
    feature_names = num_cols + cat_cols

    plt.figure(figsize=(10, 6))
    if hasattr(best_model_fitted, 'feature_importances_'):
        importances = best_model_fitted.feature_importances_
        indices = np.argsort(importances)[::-1]

        sns.barplot(x=importances[indices], y=np.array(feature_names)[indices], hue=np.array(feature_names)[indices], legend=False, palette='viridis')
        plt.title(f'Feature Importances ({best_model_name})')
        plt.xlabel('Importance')
        plt.tight_layout()
        plt.savefig(output_paths['feature_importance'], dpi=300)
        plt.close()
    else:
        importances = np.abs(best_model_fitted.coef_[0])
        indices = np.argsort(importances)[::-1]

        sns.barplot(x=importances[indices], y=np.array(feature_names)[indices], hue=np.array(feature_names)[indices], legend=False, palette='viridis')
        plt.title(f'Feature Importances (Absolute Coefficients - {best_model_name})')
        plt.xlabel('Absolute Coefficient Value')
        plt.tight_layout()
        plt.savefig(output_paths['feature_importance'], dpi=300)
        plt.close()
