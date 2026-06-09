import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve
from sklearn.model_selection import learning_curve

# Matplotlib global settings for clarity
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300
})

VIS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualizations')
os.makedirs(VIS_DIR, exist_ok=True)

def plot_confusion_matrix(y_true, y_pred, dataset_name):
    """Plots and saves confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'Confusion Matrix - {dataset_name}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, f'cm_{dataset_name}.png'))
    plt.close()

def plot_roc_curve(y_true, y_proba, dataset_name):
    """Plots and saves ROC curve."""
    if len(np.unique(y_true)) > 1:
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)

        plt.figure(figsize=(6, 5))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {dataset_name}')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, f'roc_{dataset_name}.png'))
        plt.close()

def plot_pr_curve(y_true, y_proba, dataset_name):
    """Plots and saves Precision-Recall curve."""
    if len(np.unique(y_true)) > 1:
        precision, recall, _ = precision_recall_curve(y_true, y_proba)

        plt.figure(figsize=(6, 5))
        plt.plot(recall, precision, color='blue', lw=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - {dataset_name}')
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, f'pr_{dataset_name}.png'))
        plt.close()

def plot_learning_curve(model, X, y, dataset_name):
    """Plots and saves Learning Curve."""
    train_sizes, train_scores, test_scores = learning_curve(
        model, X, y, cv=5, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 5), scoring='f1'
    )

    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)

    plt.figure(figsize=(8, 6))
    plt.plot(train_sizes, train_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, test_mean, 'o-', color="g", label="Cross-validation score")

    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_mean - test_std, test_mean + test_std, alpha=0.1, color="g")

    plt.xlabel("Training examples")
    plt.ylabel("F1 Score")
    plt.title(f"Learning Curve - {dataset_name}")
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, f'learning_curve_{dataset_name}.png'))
    plt.close()

import shap

def plot_shap_summary(shap_values, X_test, feature_names, dataset_name):
    """Generates and saves SHAP summary plot."""
    plt.figure()
    # shap.summary_plot handles its own figure creation, so we just clear and save
    plt.clf()
    shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, f'shap_summary_{dataset_name}.png'))
    plt.close()

def plot_lime_bar(lime_values, feature_names, dataset_name):
    """
    Generates a bar chart of average absolute LIME importances.
    This provides a global view of LIME explanations for the dataset.
    """
    mean_abs_lime = np.mean(np.abs(lime_values), axis=0)

    # Sort features
    idx = np.argsort(mean_abs_lime)[-10:] # Top 10

    plt.figure(figsize=(8, 6))
    plt.barh(range(len(idx)), mean_abs_lime[idx], align='center')
    plt.yticks(range(len(idx)), [feature_names[i] for i in idx])
    plt.xlabel('Mean Absolute LIME value')
    plt.title(f'LIME Feature Importance - {dataset_name}')
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, f'lime_bar_{dataset_name}.png'))
    plt.close()

def plot_metric_comparisons(results_df):
    """
    Plots cross-domain metric comparison grouped bar charts (SHAP vs LIME).
    """
    metrics = ['Fidelity', 'Stability_0.01', 'Simplicity', 'Relevance', 'Q_Score']

    for metric in metrics:
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Dataset', y=metric, hue='Method', data=results_df, ci='sd')
        plt.title(f'{metric} Comparison across Datasets')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, f'comparison_{metric}.png'))
        plt.close()

def plot_stability_vs_sigma(results_df):
    """Plots Stability vs Sigma for sensitivity analysis."""
    # Assuming the results_df passed here has rows for each sigma
    # For now, we only calculated sigma=0.01 in the main loop to save time,
    # but let's assume we pass a dataframe with 'Sigma' and 'Stability' columns
    if 'Sigma' in results_df.columns:
        plt.figure(figsize=(8, 6))
        sns.lineplot(x='Sigma', y='Stability', hue='Method', data=results_df, marker='o')
        plt.title('Stability vs Noise level (\u03C3)')
        plt.xlabel('Noise level (\u03C3)')
        plt.ylabel('Stability')
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, 'stability_vs_sigma.png'))
        plt.close()

def plot_ablation_study(ablation_df):
    """Plots Ablation study bar chart."""
    # Melt the dataframe for seaborn
    melted = pd.melt(ablation_df, id_vars=['Method'],
                     value_vars=['Full_Q', 'No_Fidelity_Q', 'No_Stability_Q', 'No_Simplicity_Q', 'No_Relevance_Q'],
                     var_name='Configuration', value_name='Q_Score')

    plt.figure(figsize=(12, 6))
    sns.barplot(x='Configuration', y='Q_Score', hue='Method', data=melted)
    plt.title('Ablation Study - Impact on Q Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, 'ablation_study.png'))
    plt.close()
