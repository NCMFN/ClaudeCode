import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    average_precision_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

def train_model(X_train, y_train, seed=42):
    """
    Trains a Random Forest classifier with n_estimators=100.
    """
    model = RandomForestClassifier(n_estimators=100, random_state=seed, n_jobs=-1)
    model.fit(X_train, y_train)
    return model

def evaluate_cv(model, X_train, y_train, cv=5):
    """
    Generates 5-fold cross-validation scores.
    """
    cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='f1')
    return cv_scores

def evaluate_model(model, X_test, y_test, dataset_name):
    """
    Evaluates the model on test data, calculates metrics,
    prints classification report, and flags suspicious scores.
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    # Handle edge case where there is only one class in y_test
    if len(np.unique(y_test)) > 1:
        roc_auc = roc_auc_score(y_test, y_proba)
    else:
        roc_auc = np.nan

    pr_auc = average_precision_score(y_test, y_proba)

    print(f"\n--- Model Evaluation for {dataset_name} ---")
    print(classification_report(y_test, y_pred, zero_division=0))

    metrics = {
        'Accuracy': acc,
        'Precision': prec,
        'Recall': rec,
        'F1_Score': f1,
        'ROC_AUC': roc_auc,
        'PR_AUC': pr_auc
    }

    # Flag suspicious scores
    if f1 > 0.99 and dataset_name in ['CC_Fraud', 'Loan_Default', 'Financial_Distress']:
        print(f"⚠️  WARNING: Suspiciously high F1-score ({f1:.4f}) on imbalanced dataset {dataset_name}.")
        print("This could indicate data leakage, trivial feature correlation, or severe class imbalance dominating predictions.")

    return metrics, y_pred, y_proba
