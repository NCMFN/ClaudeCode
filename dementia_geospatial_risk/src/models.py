import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score, precision_score, recall_score, balanced_accuracy_score, cohen_kappa_score, confusion_matrix
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
import optuna
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path("dementia_geospatial_risk/data")
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = Path("dementia_geospatial_risk/outputs")
TABLES_DIR = OUTPUTS_DIR / "tables"
TABLES_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR = OUTPUTS_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def get_data():
    df = pd.read_csv(PROCESSED_DIR / "model_ready_data.csv", dtype={'FIPS': str})

    drop_cols = ['FIPS', 'GEOID', 'NAME', 'STATEFP', 'latitude', 'longitude', 'pm25_mean', '_STATE', 'scd_prevalence', 'state_fips']
    X = df.drop(columns=[c for c in drop_cols if c in df.columns] + ['target_risk_class'])
    y = df['target_risk_class']

    # XGBoost requires classes to be exactly 0, 1, 2 etc. if some are missing, it throws error.
    # Let's check unique values and re-encode if necessary, but tertiles should give 0,1,2
    le = LabelEncoder()
    y = pd.Series(le.fit_transform(y))

    return X, y, df

def objective_xgb(trial, X, y):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'random_state': 42
    }

    clf = XGBClassifier(**params)
    pipeline = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('clf', clf)
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_val)
        scores.append(f1_score(y_val, y_pred, average='macro'))

    return np.mean(scores)

def objective_rf(trial, X, y):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 20),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
        'random_state': 42
    }

    clf = RandomForestClassifier(**params)
    pipeline = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('clf', clf)
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_val)
        scores.append(f1_score(y_val, y_pred, average='macro'))

    return np.mean(scores)

def objective_svm(trial, X, y):
    params = {
        'C': trial.suggest_float('C', 1e-3, 100, log=True),
        'gamma': trial.suggest_categorical('gamma', ['scale', 'auto']),
        'random_state': 42
    }

    clf = SVC(kernel='rbf', **params)
    pipeline = ImbPipeline([
        ('smote', SMOTE(random_state=42)),
        ('clf', clf)
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []

    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_val)
        scores.append(f1_score(y_val, y_pred, average='macro'))

    return np.mean(scores)

def evaluate_model(model_name, pipeline, X, y):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    metrics = {'macro_f1': [], 'bal_acc': [], 'kappa': []}

    y_true_all = []
    y_pred_all = []

    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_val)

        metrics['macro_f1'].append(f1_score(y_val, y_pred, average='macro'))
        metrics['bal_acc'].append(balanced_accuracy_score(y_val, y_pred))
        metrics['kappa'].append(cohen_kappa_score(y_val, y_pred))

        y_true_all.extend(y_val)
        y_pred_all.extend(y_pred)

    pipeline.fit(X, y)
    joblib.dump(pipeline, MODELS_DIR / f"best_{model_name}_model.pkl")

    cm = confusion_matrix(y_true_all, y_pred_all)
    np.save(MODELS_DIR / f"{model_name}_cm.npy", cm)

    return {
        'Model': model_name,
        'Macro-F1 Score': np.mean(metrics['macro_f1']),
        'Balanced Accuracy': np.mean(metrics['bal_acc']),
        'Cohen Kappa': np.mean(metrics['kappa'])
    }

def run_training():
    X, y, df = get_data()

    counts = y.value_counts()
    min_samples = counts.min()

    # We will use Optuna n_trials=100 per model as requested in prompt for HPO
    print("Training XGBoost...")
    study_xgb = optuna.create_study(direction='maximize')
    study_xgb.optimize(lambda t: objective_xgb(t, X, y), n_trials=100)
    study_xgb.trials_dataframe().to_csv(TABLES_DIR / "optuna_study_XGBoost.csv")

    best_xgb = XGBClassifier(**study_xgb.best_params)
    pipeline_xgb = ImbPipeline([('smote', SMOTE(random_state=42, k_neighbors=min(5, min_samples-1) if min_samples-1 > 0 else 1)), ('clf', best_xgb)])

    print("Training Random Forest...")
    study_rf = optuna.create_study(direction='maximize')
    study_rf.optimize(lambda t: objective_rf(t, X, y), n_trials=100)
    study_rf.trials_dataframe().to_csv(TABLES_DIR / "optuna_study_RandomForest.csv")

    best_rf = RandomForestClassifier(**study_rf.best_params)
    pipeline_rf = ImbPipeline([('smote', SMOTE(random_state=42, k_neighbors=min(5, min_samples-1) if min_samples-1 > 0 else 1)), ('clf', best_rf)])

    print("Training SVM...")
    study_svm = optuna.create_study(direction='maximize')
    study_svm.optimize(lambda t: objective_svm(t, X, y), n_trials=100)
    study_svm.trials_dataframe().to_csv(TABLES_DIR / "optuna_study_SVM.csv")

    best_svm = SVC(kernel='rbf', **study_svm.best_params)
    pipeline_svm = ImbPipeline([('smote', SMOTE(random_state=42, k_neighbors=min(5, min_samples-1) if min_samples-1 > 0 else 1)), ('clf', best_svm)])

    results = []
    results.append(evaluate_model('XGBoost', pipeline_xgb, X, y))
    results.append(evaluate_model('Random Forest', pipeline_rf, X, y))
    results.append(evaluate_model('SVM', pipeline_svm, X, y))

    df_results = pd.DataFrame(results)
    df_results.to_csv(TABLES_DIR / "model_comparison.csv", index=False)

    with open(TABLES_DIR / "model_comparison.tex", "w") as f:
        f.write(df_results.to_latex(index=False))

    print("Training complete. Results saved.")

if __name__ == "__main__":
    run_training()
