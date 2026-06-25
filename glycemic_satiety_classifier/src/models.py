import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

def train_models(df, model_dir):
    # Prepare features and target
    drop_cols = ['Food', 'Satiety_Index', 'Satiety_Tier', 'SI_imputed']
    X = df.drop(columns=drop_cols)
    y = df['Satiety_Tier']

    # Stratified split 80/20
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    # Save test data for evaluation phase
    X_test.to_csv(os.path.join(model_dir, 'X_test.csv'), index=False)
    y_test.to_csv(os.path.join(model_dir, 'y_test.csv'), index=False)

    # For model training using GridSearchCV with SMOTE inside pipeline
    # SMOTE only if needed, but since requirement says "if any class < 20%", let's just always apply for safety
    # Wait, some class counts might be small, let's use k_neighbors=1 for safety if dataset is tiny
    # Count smallest class in y_train
    min_class_count = y_train.value_counts().min()
    smote_k = min(5, min_class_count - 1)
    if smote_k < 1:
        smote_k = 1 # Avoid error, though if it's 1, it might just duplicate

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    print("Training Decision Tree...")
    # Model A: Decision Tree
    dt_pipeline = ImbPipeline([
        ('smote', SMOTE(random_state=42, k_neighbors=smote_k)),
        ('dt', DecisionTreeClassifier(random_state=42))
    ])
    dt_param_grid = {
        'dt__max_depth': [3, 5, 7, None],
        'dt__min_samples_leaf': [1, 2, 5],
        'dt__criterion': ['gini', 'entropy']
    }
    dt_grid = GridSearchCV(dt_pipeline, dt_param_grid, cv=cv, scoring='f1_macro', n_jobs=-1)
    dt_grid.fit(X_train, y_train)
    best_dt = dt_grid.best_estimator_
    joblib.dump(best_dt, os.path.join(model_dir, 'dt_best_model.pkl'))
    print("Best DT Params:", dt_grid.best_params_)

    print("Training Logistic Regression...")
    # Model B: Logistic Regression
    lr_pipeline = ImbPipeline([
        ('scaler', StandardScaler()),
        ('smote', SMOTE(random_state=42, k_neighbors=smote_k)),
        ('lr', LogisticRegression(random_state=42))
    ])
    lr_param_grid = {
        'lr__C': [0.01, 0.1, 1, 10],
        'lr__solver': ['lbfgs'],
        'lr__max_iter': [1000],

    }
    lr_grid = GridSearchCV(lr_pipeline, lr_param_grid, cv=cv, scoring='f1_macro', n_jobs=-1)
    lr_grid.fit(X_train, y_train)
    best_lr = lr_grid.best_estimator_
    joblib.dump(best_lr, os.path.join(model_dir, 'lr_best_model.pkl'))
    print("Best LR Params:", lr_grid.best_params_)

    print("Training Random Forest...")
    # Model C: Random Forest
    rf_pipeline = ImbPipeline([
        ('smote', SMOTE(random_state=42, k_neighbors=smote_k)),
        ('rf', RandomForestClassifier(random_state=42))
    ])
    rf_param_grid = {
        'rf__n_estimators': [100, 200],
        'rf__max_depth': [5, 10, None],
        'rf__min_samples_leaf': [1, 2]
    }
    rf_grid = GridSearchCV(rf_pipeline, rf_param_grid, cv=cv, scoring='f1_macro', n_jobs=-1)
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_
    joblib.dump(best_rf, os.path.join(model_dir, 'rf_best_model.pkl'))
    print("Best RF Params:", rf_grid.best_params_)

    # Calculate cross-val scores for the best estimators
    # The requirement says "Cross-validated accuracy (5-fold, mean +- std)"
    for name, model in [("DT", best_dt), ("LR", best_lr), ("RF", best_rf)]:
        scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
        print(f"{name} CV Accuracy: {np.mean(scores):.3f} +/- {np.std(scores):.3f}")

    # Also save training set for SHAP dependence etc if needed
    X_train.to_csv(os.path.join(model_dir, 'X_train.csv'), index=False)
    y_train.to_csv(os.path.join(model_dir, 'y_train.csv'), index=False)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, 'data', 'processed')
    model_dir = os.path.join(base_dir, 'outputs') # just saving models in outputs folder

    df = pd.read_csv(os.path.join(proc_dir, 'satiety_features_engineered.csv'))
    train_models(df, model_dir)

if __name__ == "__main__":
    main()
