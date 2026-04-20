import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, accuracy_score, roc_auc_score
from sklearn.ensemble import IsolationForest
import os

def train_xgboost(X_train, y_train, X_test, y_test, output_model_path: str):
    print("Training XGBoost Classifier...")
    xgb = XGBClassifier(
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )

    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [4, 6, 8],
        'learning_rate': [0.05, 0.1, 0.2],
        'subsample': [0.8, 1.0],
        'colsample_bytree': [0.8, 1.0],
        'min_child_weight': [1, 3]
    }

    grid_search = GridSearchCV(
        estimator=xgb,
        param_grid=param_grid,
        scoring='f1',
        cv=5,
        verbose=1,
        n_jobs=-1
    )

    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    print(f"Best XGBoost params: {grid_search.best_params_}")

    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    metrics = {
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'accuracy': accuracy_score(y_test, y_pred),
        'auc_roc': roc_auc_score(y_test, y_proba)
    }

    print("\n--- XGBoost Test Metrics ---")
    for k, v in metrics.items():
        print(f"{k.capitalize()}: {v:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    joblib.dump(best_model, output_model_path)
    print(f"Model saved to {output_model_path}")

    return best_model, metrics

def train_isolation_forest(X_train, X_test, y_test):
    print("Training Isolation Forest Anomaly Detection...")
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.15,
        random_state=42
    )

    iso_forest.fit(X_train)
    y_pred_if_raw = iso_forest.predict(X_test)
    y_pred_if = [1 if x == -1 else 0 for x in y_pred_if_raw]

    metrics = {
        'precision': precision_score(y_test, y_pred_if, zero_division=0),
        'recall': recall_score(y_test, y_pred_if, zero_division=0),
        'f1': f1_score(y_test, y_pred_if, zero_division=0)
    }

    print("\n--- Isolation Forest Test Metrics ---")
    for k, v in metrics.items():
        print(f"{k.capitalize()}: {v:.4f}")

    return iso_forest, metrics, y_pred_if
