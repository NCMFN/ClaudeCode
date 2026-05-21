"""Metrics, confusion matrix, A/B test."""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve, auc
from sklearn.model_selection import train_test_split
import config
import logging
from feature_engineering import apply_smote
from model_training import get_models

# Ensure strict logging for Python projects
os.makedirs('results/logs', exist_ok=True)
logging.basicConfig(
    filename='results/logs/run.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def rule_based_baseline(df):
    preds = np.zeros(len(df))
    condition = (df['pH'] < 4.5) | (df['pH'] > 8.5) | (df['Soil_Moisture'] < 10)
    preds[condition] = 1
    return preds

def evaluate_models(X_test, y_test, X_test_raw_df=None):
    models_dict = get_models()
    results = []

    plt.figure(1, figsize=(10, 8))

    for name in models_dict.keys():
        model_path = os.path.join(config.MODELS_DIR, f"{name.replace(' ', '_').lower()}.pkl")
        if not os.path.exists(model_path):
            logging.error(f"Model file not found: {model_path}")
            continue

        model = joblib.load(model_path)
        y_pred = model.predict(X_test)

        has_proba = False
        try:
            y_proba = model.predict_proba(X_test)[:, 1]
            auc_val = roc_auc_score(y_test, y_proba)

            plt.figure(1)
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            plt.plot(fpr, tpr, label=f"{name} (AUC = {auc_val:.3f})")
            has_proba = True
        except AttributeError:
            auc_val = np.nan
            logging.warning(f"AUC not calculable for {name}")

        f1 = f1_score(y_test, y_pred, average='weighted')
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted')

        print(f"--- {name} ---")
        print(classification_report(y_test, y_pred, zero_division=0))
        logging.info(f"{name} Metrics: F1={f1:.3f}, Precision={precision:.3f}, Recall={recall:.3f}, AUC={auc_val}")

        results.append({
            'Model': name,
            'F1_Score_Weighted': f1,
            'Precision': precision,
            'Recall': recall,
            'ROC_AUC': auc_val
        })

        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'{name} Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(config.PLOTS_DIR, f"{name.replace(' ', '_').lower()}_cm.png"))
        plt.close()

        if has_proba:
            precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_proba)
            pr_auc = auc(recall_vals, precision_vals)
            plt.figure(figsize=(6, 5))
            plt.plot(recall_vals, precision_vals, label=f'PR curve (AUC = {pr_auc:.3f})')
            plt.xlabel('Recall')
            plt.ylabel('Precision')
            plt.title(f'{name} Precision-Recall Curve')
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(config.PLOTS_DIR, f"{name.replace(' ', '_').lower()}_pr.png"))
            plt.close()

            plt.figure(figsize=(6, 5))
            sns.histplot(y_proba, bins=20, kde=True)
            plt.title(f'{name} Predicted Probability Distribution')
            plt.xlabel('Predicted Probability')
            plt.tight_layout()
            plt.savefig(os.path.join(config.PLOTS_DIR, f"{name.replace(' ', '_').lower()}_prob_dist.png"))
            plt.close()

        if name in ['Random Forest', 'XGBoost', 'Decision Tree']:
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]
            top_features = X_test.columns[indices]

            plt.figure(figsize=(10, 6))
            plt.title(f'Top 10 Feature Importances ({name})')
            plt.bar(range(10), importances[indices], align='center')
            plt.xticks(range(10), top_features, rotation=45, ha='right')
            plt.tight_layout()

            filename = 'rf' if name == 'Random Forest' else ('xgb' if name == 'XGBoost' else 'dt')
            plt.savefig(os.path.join(config.PLOTS_DIR, f'{filename}_feature_importance.png'))
            plt.close()

    if X_test_raw_df is not None:
        y_pred_baseline = rule_based_baseline(X_test_raw_df)
        f1_baseline = f1_score(y_test, y_pred_baseline, average='weighted')

        best_ml_f1 = max([r['F1_Score_Weighted'] for r in results])
        improvement = (best_ml_f1 - f1_baseline) / f1_baseline if f1_baseline > 0 else 0

        precision_base = precision_score(y_test, y_pred_baseline, average='weighted', zero_division=0)
        recall_base = recall_score(y_test, y_pred_baseline, average='weighted')

        print(f"--- Rule-Based Baseline ---")
        print(classification_report(y_test, y_pred_baseline, zero_division=0))

        results.append({
            'Model': 'Rule-Based Baseline',
            'F1_Score_Weighted': f1_baseline,
            'Precision': precision_base,
            'Recall': recall_base,
            'ROC_AUC': np.nan
        })

        cm_base = confusion_matrix(y_test, y_pred_baseline)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm_base, annot=True, fmt='d', cmap='Blues')
        plt.title('Rule-Based Baseline Confusion Matrix')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(os.path.join(config.PLOTS_DIR, 'baseline_cm.png'))
        plt.close()

        print(f"A/B Test: ML Best F1 ({best_ml_f1:.3f}) vs Baseline F1 ({f1_baseline:.3f}). Improvement: {improvement*100:.1f}%")

    plt.figure(1)
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(config.PLOTS_DIR, 'roc_curves.png'))
    plt.close()

    results_df = pd.DataFrame(results)
    results_df.to_csv(config.RESULTS_SUMMARY_PATH, index=False)
    print(f"Results saved to {config.RESULTS_SUMMARY_PATH}")

if __name__ == "__main__":
    df = pd.read_csv(config.FEATURE_DATA_PATH)

    X = df.drop(columns=['Intervention_Required'])
    y = df['Intervention_Required']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y)

    evaluate_models(X_test, y_test, X_test)
