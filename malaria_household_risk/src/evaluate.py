import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, precision_recall_curve, brier_score_loss
from sklearn.calibration import calibration_curve
import joblib
import os
from preprocess import get_train_test_data

def plot_confusion_matrix(y_true, y_pred, output_path):
    cm = confusion_matrix(y_true, y_pred)
    # Row normalize as per memory guideline
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', xticklabels=['Uninfected', 'Infected'], yticklabels=['Uninfected', 'Infected'])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Normalized Confusion Matrix')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def plot_roc_curve(models_dict, X_test, y_test, output_path):
    plt.figure(figsize=(8, 6))
    for name, model in models_dict.items():
        y_prob = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f'{name} (AUC = {roc_auc:.2f})')

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc='lower right')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def plot_pr_curve(models_dict, X_test, y_test, output_path):
    plt.figure(figsize=(8, 6))
    for name, model in models_dict.items():
        y_prob = model.predict_proba(X_test)[:, 1]
        precision, recall, _ = precision_recall_curve(y_test, y_prob)
        plt.plot(recall, precision, label=name)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc='lower left')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def plot_calibration_curve(models_dict, X_test, y_test, output_path):
    plt.figure(figsize=(8, 6))
    plt.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")

    for name, model in models_dict.items():
        y_prob = model.predict_proba(X_test)[:, 1]
        prob_true, prob_pred = calibration_curve(y_test, y_prob, n_bins=10)
        brier = brier_score_loss(y_test, y_prob)
        plt.plot(prob_pred, prob_true, marker='s', label=f'{name} (Brier={brier:.3f})')

    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives')
    plt.title('Calibration Curve (Reliability Diagram)')
    plt.legend(loc='lower right')
    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

def main():
    _, X_test, _, y_test = get_train_test_data()

    models_dir = 'outputs/models'
    figures_dir = 'outputs/figures'
    results_dir = 'outputs/results'
    os.makedirs(results_dir, exist_ok=True)

    lr = joblib.load(os.path.join(models_dir, 'logistic_regression.pkl'))
    dt = joblib.load(os.path.join(models_dir, 'decision_tree.pkl'))
    rf = joblib.load(os.path.join(models_dir, 'random_forest.pkl'))

    models = {'Logistic Regression': lr, 'Decision Tree': dt, 'Random Forest': rf}

    reports = []

    for name, model in models.items():
        print(f"\n=== Evaluating {name} ===")
        y_pred = model.predict(X_test)

        report_dict = classification_report(y_test, y_pred, output_dict=True)
        report_df = pd.DataFrame(report_dict).transpose()
        report_df['model'] = name
        reports.append(report_df)

        print(classification_report(y_test, y_pred))

        cm_path = os.path.join(figures_dir, f'confusion_matrix_{name.replace(" ", "_").lower()}.png')
        plot_confusion_matrix(y_test, y_pred, cm_path)

    final_report = pd.concat(reports)
    final_report.to_csv(os.path.join(results_dir, 'classification_reports.csv'))

    plot_roc_curve(models, X_test, y_test, os.path.join(figures_dir, 'roc_curve.png'))
    plot_pr_curve(models, X_test, y_test, os.path.join(figures_dir, 'pr_curve.png'))
    plot_calibration_curve(models, X_test, y_test, os.path.join(figures_dir, 'calibration_curve.png'))

if __name__ == '__main__':
    main()
