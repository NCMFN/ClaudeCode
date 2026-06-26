import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
import os
from sklearn.metrics import (
    roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score,
    f1_score, confusion_matrix, classification_report
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def evaluate_model(model, X_test, y_test, mean_loan_amount, output_dir='outputs'):
    """
    Evaluates the trained model on test data and saves plots/reports.
    """
    os.makedirs(output_dir, exist_ok=True)

    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    # 1. AUC-ROC
    auc_roc = roc_auc_score(y_test, y_pred_proba)
    logging.info(f"AUC-ROC Score: {auc_roc:.4f}")

    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'AUC = {auc_roc:.4f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.title('ROC Curve')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc='lower right')
    plt.savefig(os.path.join(output_dir, 'roc_curve.png'))
    plt.close()

    # 2. PR Curve & AP
    ap_score = average_precision_score(y_test, y_pred_proba)
    logging.info(f"Average Precision Score: {ap_score:.4f}")

    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, label=f'AP = {ap_score:.4f}')
    plt.title('Precision-Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.legend(loc='lower left')
    plt.savefig(os.path.join(output_dir, 'pr_curve.png'))
    plt.close()

    # 3. F1 Scores
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_default = f1_score(y_test, y_pred)
    logging.info(f"F1-Score (Macro): {f1_macro:.4f}")
    logging.info(f"F1-Score (Default Class): {f1_default:.4f}")

    # 4. Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Safe (0)', 'Default (1)'],
                yticklabels=['Safe (0)', 'Default (1)'])
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.text(0.5, 0.2, f"TN: {tn}\nFP: {fp}", ha='center', va='center', color='black')
    plt.text(1.5, 1.2, f"FN: {fn}\nTP: {tp}", ha='center', va='center', color='black')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()

    # 5. Classification Report
    report = classification_report(y_test, y_pred, target_names=['Safe', 'Default'])
    logging.info(f"Classification Report:\n{report}")

    # 6. Business Metric (Type II Errors)
    missed_defaults = fn
    principal_at_risk = missed_defaults * mean_loan_amount
    business_msg = f"Missed defaults (FN): {missed_defaults} — representing ${principal_at_risk:,.2f} in potential principal at risk"
    logging.info(business_msg)

    # Save text report
    report_path = os.path.join(output_dir, 'evaluation_report.txt')
    with open(report_path, 'w') as f:
        f.write(f"AUC-ROC Score: {auc_roc:.4f}\n")
        f.write(f"Average Precision Score: {ap_score:.4f}\n")
        f.write(f"F1-Score (Macro): {f1_macro:.4f}\n")
        f.write(f"F1-Score (Default Class): {f1_default:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
        f.write("\n\nBusiness Impact:\n")
        f.write(business_msg + "\n")

    logging.info(f"Evaluation report saved to {report_path}")

if __name__ == "__main__":
    pass
