import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, roc_auc_score, roc_curve, precision_recall_curve, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import os

def train_baselines_and_evaluate(X_train, y_train, X_train_sm, y_train_sm, X_test, y_test, xgb_model, if_model, output_csv: str):
    print("Training Baselines...")

    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)

    rf = RandomForestClassifier(n_estimators=200, random_state=42)
    rf.fit(X_train_sm, y_train_sm)

    models = {
        'XGBoost': xgb_model,
        'Random Forest': rf,
        'Logistic Regression': lr
    }

    results = []

    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        results.append({
            'Model': name,
            'Precision': precision_score(y_test, y_pred),
            'Recall': recall_score(y_test, y_pred),
            'F1-Score': f1_score(y_test, y_pred),
            'Accuracy': accuracy_score(y_test, y_pred),
            'AUC-ROC': roc_auc_score(y_test, y_proba)
        })

    y_pred_if_raw = if_model.predict(X_test)
    y_pred_if = [1 if x == -1 else 0 for x in y_pred_if_raw]

    results.append({
        'Model': 'Isolation Forest',
        'Precision': precision_score(y_test, y_pred_if, zero_division=0),
        'Recall': recall_score(y_test, y_pred_if, zero_division=0),
        'F1-Score': f1_score(y_test, y_pred_if, zero_division=0),
        'Accuracy': accuracy_score(y_test, y_pred_if),
        'AUC-ROC': None
    })

    df_results = pd.DataFrame(results)
    print("\n--- Model Comparison Table ---")
    print(df_results)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_results.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

    return models, df_results

def plot_evaluation(models, if_model, X_test, y_test, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(8, 6))
    for name, model in models.items():
        y_proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        auc = roc_auc_score(y_test, y_proba)
        plt.plot(fpr, tpr, label=f'{name} (AUC = {auc:.3f})')

    y_scores_if = -if_model.decision_function(X_test)
    fpr_if, tpr_if, _ = roc_curve(y_test, y_scores_if)
    auc_if = roc_auc_score(y_test, y_scores_if)
    plt.plot(fpr_if, tpr_if, label=f'Isolation Forest (AUC = {auc_if:.3f})', linestyle='--')

    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve Comparison')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'roc_curve_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(8, 6))
    for name in ['XGBoost', 'Random Forest']:
        y_proba = models[name].predict_proba(X_test)[:, 1]
        precision, recall, _ = precision_recall_curve(y_test, y_proba)
        plt.plot(recall, precision, label=name)

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc='lower left')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'precision_recall_curve.png'), dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(6, 5))
    xgb_pred = models['XGBoost'].predict(X_test)
    cm = confusion_matrix(y_test, xgb_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix - XGBoost')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix_xgb.png'), dpi=300, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(10, 8))
    xgb = models['XGBoost']
    importances = xgb.feature_importances_
    features = X_test.columns
    df_imp = pd.DataFrame({'Feature': features, 'Importance': importances}).sort_values('Importance', ascending=False).head(15)
    sns.barplot(x='Importance', y='Feature', data=df_imp)
    plt.title('Top 15 Features by XGBoost Gain')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feature_importance_xgb.png'), dpi=300, bbox_inches='tight')
    plt.close()
