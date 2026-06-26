import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
import matplotlib.pyplot as plt
import joblib
import os
from preprocess import get_train_test_data, preprocess_input

def evaluate_cv(model, X, y, cv=5):
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    scores = cross_validate(model, X, y, cv=skf, scoring=scoring, return_estimator=True)

    metrics_summary = {}
    print(f"\n--- Cross-Validation Results for {model.__class__.__name__} ---")
    for metric in scoring:
        mean_score = np.mean(scores[f'test_{metric}'])
        std_score = np.std(scores[f'test_{metric}'])
        metrics_summary[metric] = f"{mean_score:.4f} ± {std_score:.4f}"
        print(f"{metric.capitalize()}: {metrics_summary[metric]}")

    # Fit final model on full data
    model.fit(X, y)
    return model, metrics_summary

def score_household(input_dict, model_path='malaria_household_risk/outputs/models/logistic_regression.pkl'):
    model = joblib.load(model_path)
    X_processed = preprocess_input(input_dict)

    prob = model.predict_proba(X_processed)[0, 1]
    pred = model.predict(X_processed)[0]

    if prob < 0.3:
        risk_tier = 'Low'
    elif prob <= 0.6:
        risk_tier = 'Medium'
    else:
        risk_tier = 'High'

    return {
        'predicted_class': int(pred),
        'infection_probability': float(prob),
        'risk_tier': risk_tier
    }

def main():
    X_train, X_test, y_train, y_test = get_train_test_data()

    models_dir = 'outputs/models'
    figures_dir = 'outputs/figures'
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # Model 1: Logistic Regression
    lr = LogisticRegression(class_weight='balanced', max_iter=1000, C=1.0, random_state=42)
    lr, _ = evaluate_cv(lr, X_train, y_train)

    print("\n--- Logistic Regression Odds Ratios ---")
    odds_ratios = np.exp(lr.coef_[0])
    for feature, odds in zip(X_train.columns, odds_ratios):
        print(f"{feature}: {odds:.4f}")

    joblib.dump(lr, os.path.join(models_dir, 'logistic_regression.pkl'))

    # Model 2: Decision Tree
    dt = DecisionTreeClassifier(max_depth=5, criterion='gini', class_weight='balanced', random_state=42)
    dt, _ = evaluate_cv(dt, X_train, y_train)

    print("\n--- Decision Tree Rules ---")
    tree_rules = export_text(dt, feature_names=list(X_train.columns))
    print(tree_rules)

    plt.figure(figsize=(20, 10))
    plot_tree(dt, feature_names=list(X_train.columns), class_names=['Uninfected', 'Infected'], filled=True)
    plt.savefig(os.path.join(figures_dir, 'decision_tree.png'))
    plt.close()

    joblib.dump(dt, os.path.join(models_dir, 'decision_tree.pkl'))

    # Optional Models
    rf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    rf, _ = evaluate_cv(rf, X_train, y_train)
    joblib.dump(rf, os.path.join(models_dir, 'random_forest.pkl'))

    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb, _ = evaluate_cv(gb, X_train, y_train)
    joblib.dump(gb, os.path.join(models_dir, 'gradient_boosting.pkl'))

if __name__ == '__main__':
    main()
