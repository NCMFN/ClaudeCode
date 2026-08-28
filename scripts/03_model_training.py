import pandas as pd
import numpy as np
import yaml
import os
import time
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score, recall_score, make_scorer
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import lightgbm as lgb
import optuna
import shap

# Disable optuna output
optuna.logging.set_verbosity(optuna.logging.WARNING)

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

processed_dir = config['data']['processed_dir']
tables_dir = config['data']['tables_dir']
figures_dir = config['data']['figures_dir']
seed = config['random_seed']
folds = config['models']['cv_folds']

df = pd.read_parquet(os.path.join(processed_dir, 'features_labeled.parquet'))
X = df.drop(columns=['state'])
y = df['state']

# XGBoost strictly requires labels 0 to num_classes-1
le = LabelEncoder()
y = pd.Series(le.fit_transform(y), index=y.index)
joblib.dump(le, os.path.join(processed_dir, 'label_encoder.pkl'))

skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)

baseline_results = []
ensemble_results = []
latency_results = []

def evaluate_model(model, X_test, y_test, name, fold):
    start_time = time.perf_counter()
    preds = model.predict(X_test)
    end_time = time.perf_counter()
    latency = (end_time - start_time) / len(X_test) * 1000 # ms per record

    preds_proba = model.predict_proba(X_test)
    f1 = f1_score(y_test, preds, average='macro')
    # Use OvR for multi-class ROC-AUC
    try:
        roc_auc = roc_auc_score(y_test, preds_proba, multi_class='ovr', average='macro')
    except Exception as e:
        roc_auc = np.nan
    recalls = recall_score(y_test, preds, average=None)

    return {
        'model': name,
        'fold': fold,
        'f1': f1,
        'roc_auc': roc_auc,
        'latency_ms': latency,
        'recall_0': recalls[0] if len(recalls) > 0 else 0,
        'recall_1': recalls[1] if len(recalls) > 1 else 0,
        'recall_2': recalls[2] if len(recalls) > 2 else 0,
        'recall_3': recalls[3] if len(recalls) > 3 else 0,
    }

print("Running Baselines...")
for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
    print(f"Fold {fold} Baselines")
    X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
    X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

    # SMOTE only on train
    smote = SMOTE(random_state=seed)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    # Decision Tree
    dt = DecisionTreeClassifier(random_state=seed)
    dt.fit(X_train_res, y_train_res)
    baseline_results.append(evaluate_model(dt, X_test, y_test, 'DecisionTree', fold))

    # Random Forest
    rf = RandomForestClassifier(random_state=seed)
    rf.fit(X_train_res, y_train_res)
    baseline_results.append(evaluate_model(rf, X_test, y_test, 'RandomForest', fold))

print("Running Ensembles with Optuna...")
def objective_xgb(trial, X_train, y_train, X_test, y_test):
    params = {
        'learning_rate': trial.suggest_float('learning_rate', config['models']['xgboost']['learning_rate'][0], config['models']['xgboost']['learning_rate'][1], log=True),
        'max_depth': trial.suggest_int('max_depth', config['models']['xgboost']['max_depth'][0], config['models']['xgboost']['max_depth'][1]),
        'subsample': trial.suggest_float('subsample', config['models']['xgboost']['subsample'][0], config['models']['xgboost']['subsample'][1]),
        'n_estimators': trial.suggest_int('n_estimators', config['models']['xgboost']['n_estimators'][0], config['models']['xgboost']['n_estimators'][1]),
        'random_state': seed,
        'eval_metric': 'mlogloss',
        'n_jobs': -1
    }
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return f1_score(y_test, preds, average='macro')

def objective_lgb(trial, X_train, y_train, X_test, y_test):
    params = {
        'learning_rate': trial.suggest_float('learning_rate', config['models']['lightgbm']['learning_rate'][0], config['models']['lightgbm']['learning_rate'][1], log=True),
        'max_depth': trial.suggest_int('max_depth', config['models']['lightgbm']['max_depth'][0], config['models']['lightgbm']['max_depth'][1]),
        'subsample': trial.suggest_float('subsample', config['models']['lightgbm']['subsample'][0], config['models']['lightgbm']['subsample'][1]),
        'n_estimators': trial.suggest_int('n_estimators', config['models']['lightgbm']['n_estimators'][0], config['models']['lightgbm']['n_estimators'][1]),
        'random_state': seed,
        'verbose': -1,
        'n_jobs': -1
    }
    model = lgb.LGBMClassifier(**params)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return f1_score(y_test, preds, average='macro')

best_models = {}
all_results = pd.DataFrame()

xgb_studies = []

# Subsample dataset for optuna to speed things up
df_sample = df.sample(frac=0.2, random_state=seed)
X_opt = df_sample.drop(columns=['state'])
y_opt = le.transform(df_sample['state'])
y_opt = pd.Series(y_opt, index=X_opt.index)

for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
    print(f"Fold {fold} Ensembles")
    X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
    X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]

    smote = SMOTE(random_state=seed)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    if fold == 0:
        # Use subsampled data for hyperparameter search just for first fold to save time
        train_idx_opt, test_idx_opt = next(skf.split(X_opt, y_opt))
        X_train_opt, y_train_opt = X_opt.iloc[train_idx_opt], y_opt.iloc[train_idx_opt]
        X_test_opt, y_test_opt = X_opt.iloc[test_idx_opt], y_opt.iloc[test_idx_opt]
        X_train_res_opt, y_train_res_opt = smote.fit_resample(X_train_opt, y_train_opt)

        # XGBoost
        study_xgb = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=seed))
        # 5 trials per instructions
        study_xgb.optimize(lambda trial: objective_xgb(trial, X_train_res_opt, y_train_res_opt, X_test_opt, y_test_opt), n_trials=5)

        # LightGBM
        study_lgb = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=seed))
        study_lgb.optimize(lambda trial: objective_lgb(trial, X_train_res_opt, y_train_res_opt, X_test_opt, y_test_opt), n_trials=5)


    best_xgb = xgb.XGBClassifier(**study_xgb.best_params, random_state=seed, eval_metric='mlogloss', n_jobs=-1)
    best_xgb.fit(X_train_res, y_train_res)
    ensemble_results.append(evaluate_model(best_xgb, X_test, y_test, 'XGBoost', fold))
    xgb_studies.append(study_xgb)

    best_lgb = lgb.LGBMClassifier(**study_lgb.best_params, random_state=seed, verbose=-1, n_jobs=-1)
    best_lgb.fit(X_train_res, y_train_res)
    ensemble_results.append(evaluate_model(best_lgb, X_test, y_test, 'LightGBM', fold))

    if fold == 0:
        best_models['XGBoost'] = best_xgb
        best_models['LightGBM'] = best_lgb
        best_models['Study_XGBoost'] = study_xgb
        best_models['Study_LightGBM'] = study_lgb


# Save results
pd.DataFrame(baseline_results).to_csv(os.path.join(tables_dir, '05_baseline_results.csv'), index=False)
pd.DataFrame(ensemble_results).to_csv(os.path.join(tables_dir, '06_ensemble_results.csv'), index=False)
all_results = pd.concat([pd.DataFrame(baseline_results), pd.DataFrame(ensemble_results)])
os.makedirs('results', exist_ok=True)
all_results.to_csv('results/model_comparison.csv', index=False)

# Hyperparams
hyperparams = {
    'XGBoost': best_models['Study_XGBoost'].best_params,
    'LightGBM': best_models['Study_LightGBM'].best_params
}
pd.DataFrame(hyperparams).T.to_csv(os.path.join(tables_dir, '07_best_hyperparameters.csv'))

# Boxplot
plt.figure(figsize=(10, 6))
sns.boxplot(data=all_results, x='model', y='f1')
plt.title('CV Fold F1 Score Comparison')
plt.savefig(os.path.join(figures_dir, '06_cv_f1_boxplot.png'), dpi=300, bbox_inches='tight')
plt.close()

# Optuna history
from optuna.visualization.matplotlib import plot_optimization_history
plot_optimization_history(best_models['Study_XGBoost'])
plt.savefig(os.path.join(figures_dir, '07_optuna_history.png'), dpi=300, bbox_inches='tight')
plt.close()


print("Running SHAP...")
# SHAP
best_model = best_models['XGBoost'] # Assume XGBoost is best for SHAP
explainer = shap.TreeExplainer(best_model)
# Sample to save time and memory
X_sample = X.sample(min(100, len(X)), random_state=seed) # use tiny sample for shap to be fast
shap_values = explainer.shap_values(X_sample)

if isinstance(shap_values, list): # Multi-class
    shap_vals = shap_values[1] # Look at state 1 for simplicity in summary
else:
    # Some xgboost versions return (N, F, C)
    if len(shap_values.shape) == 3:
        shap_vals = shap_values[:, :, 1]
    else:
        shap_vals = shap_values

# Summary
plt.figure()
shap.summary_plot(shap_vals, X_sample, show=False)
plt.savefig(os.path.join(figures_dir, '08_shap_summary.png'), dpi=300, bbox_inches='tight')
plt.close()

# Importance table
mean_shap = np.abs(shap_vals).mean(axis=0)
top_features = pd.DataFrame({'feature': X.columns, 'importance': mean_shap}).sort_values(by='importance', ascending=False)
top_features.head(10).to_csv(os.path.join(tables_dir, '08_shap_top10.csv'), index=False)

# Dependence
top_feat = top_features.iloc[0]['feature']
plt.figure()
shap.dependence_plot(top_feat, shap_vals, X_sample, show=False)
plt.savefig(os.path.join(figures_dir, '09_shap_dependence.png'), dpi=300, bbox_inches='tight')
plt.close()

joblib.dump(best_model, os.path.join(processed_dir, 'best_model.pkl'))
print("Stage 3 Complete")
