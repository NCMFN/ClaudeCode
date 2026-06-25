import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import json

from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, cohen_kappa_score, roc_auc_score
from imblearn.over_sampling import SMOTE

warnings.filterwarnings("ignore")
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def train_and_evaluate():
    df = pd.read_csv("data/processed/features_engineered.csv")
    X = df.drop(columns=['Performance_Class'])
    y = df['Performance_Class']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    smote = SMOTE(random_state=42, k_neighbors=5)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    os.makedirs("outputs/figures", exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.countplot(x=y_train, ax=axes[0], palette='Set2', hue=y_train, legend=False)
    axes[0].set_title('Before SMOTE')
    axes[0].set_xlabel('Performance Class')
    sns.countplot(x=y_train_resampled, ax=axes[1], palette='Set2', hue=y_train_resampled, legend=False)
    axes[1].set_title('After SMOTE')
    axes[1].set_xlabel('Performance Class')
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_09_smote_balance.png')
    plt.close()

    os.makedirs("data/synthetic", exist_ok=True)
    X_train_resampled.to_csv("data/synthetic/X_train_resampled.csv", index=False)
    y_train_resampled.to_csv("data/synthetic/y_train_resampled.csv", index=False)
    X_test.to_csv("data/synthetic/X_test.csv", index=False)
    y_test.to_csv("data/synthetic/y_test.csv", index=False)

    models = {
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
        'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=50, random_state=42)
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    xgb_param_dist = {'n_estimators': [100, 300, 500], 'max_depth': [3, 5, 7], 'learning_rate': [0.01, 0.05, 0.1], 'subsample': [0.7, 0.9], 'colsample_bytree': [0.7, 1.0]}
    models['XGBoost'] = RandomizedSearchCV(XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss', verbosity=0), xgb_param_dist, n_iter=30, cv=5, scoring='f1_weighted', random_state=42, n_jobs=-1)

    lgbm_param_dist = {'num_leaves': [31, 63, 127], 'learning_rate': [0.01, 0.05, 0.1], 'n_estimators': [100, 300, 500], 'min_child_samples': [10, 20, 50]}
    models['LightGBM'] = RandomizedSearchCV(LGBMClassifier(random_state=42, verbose=-1), lgbm_param_dist, n_iter=30, cv=5, scoring='f1_weighted', random_state=42, n_jobs=-1)

    mlp_param_dist = {'hidden_layer_sizes': [(64, 32), (128, 64), (256, 128, 64)], 'activation': ['relu', 'tanh'], 'alpha': [0.0001, 0.001, 0.01], 'learning_rate_init': [0.001, 0.01]}
    models['MLP'] = RandomizedSearchCV(MLPClassifier(random_state=42, max_iter=50), mlp_param_dist, n_iter=30, cv=5, scoring='f1_weighted', random_state=42, n_jobs=-1)

    results = []
    os.makedirs("outputs/models", exist_ok=True)
    cv_scores_dict = {}

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_resampled, y_train_resampled)
        if hasattr(model, 'best_estimator_'):
            best_model = model.best_estimator_
            cv_acc_scores = cross_val_score(best_model, X_train_resampled, y_train_resampled, cv=5, scoring='accuracy')
        else:
            best_model = model
            cv_acc_scores = cross_val_score(best_model, X_train_resampled, y_train_resampled, cv=5, scoring='accuracy')

        cv_scores_dict[name] = cv_acc_scores.tolist()

        y_pred = best_model.predict(X_test)
        y_prob = best_model.predict_proba(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1_w = f1_score(y_test, y_pred, average='weighted')
        prec_w = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec_w = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        kappa = cohen_kappa_score(y_test, y_pred)
        try: roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
        except: roc_auc = np.nan

        results.append({
            'Model': name, 'Accuracy': acc, 'F1_Weighted': f1_w, 'Precision_Weighted': prec_w,
            'Recall_Weighted': rec_w, 'Cohen_Kappa': kappa, 'ROC_AUC_OvR': roc_auc,
            'Mean_CV_Accuracy': np.mean(cv_acc_scores), 'Std_CV_Accuracy': np.std(cv_acc_scores)
        })
        joblib.dump(best_model, f"outputs/models/{name}_best.pkl")

    results_df = pd.DataFrame(results)
    results_df.to_csv("outputs/tables/model_training_summary.csv", index=False)
    with open('outputs/tables/cv_scores.json', 'w') as f: json.dump(cv_scores_dict, f)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    train_and_evaluate()
