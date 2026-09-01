import pandas as pd
import numpy as np
from sklearn.model_selection import GroupShuffleSplit, train_test_split, StratifiedKFold
from sklearn.metrics import average_precision_score, f1_score, recall_score, confusion_matrix
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')
import scipy.stats as stats

# Configs
from config import RANDOM_SEED, CHRONO_TRAIN_FRAC, CHRONO_VAL_FRAC, GROUP_TRAIN_FRAC, GROUP_VAL_FRAC, RANDOM_TRAIN_FRAC, RANDOM_VAL_FRAC, SHIFT_TRAIN_FRAC, SHIFT_VAL_FRAC, SHIFT_TEST_FRAC, FEATURE_GROUPS
import os


class DummyLSTM:
    def __init__(self, random_state=42):
        self.model = MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=200, random_state=random_state)
    def fit(self, X, y):
        self.model.fit(X, y)
    def predict_proba(self, X):
        return self.model.predict_proba(X)
    def predict(self, X):
        return self.model.predict(X)

def get_models():
    return {
        'XGBoost': XGBClassifier(random_state=RANDOM_SEED, eval_metric='logloss'),
        'SVM': SVC(probability=True, random_state=RANDOM_SEED),
        'MLP': MLPClassifier(random_state=RANDOM_SEED),
        'LSTM_proxy': DummyLSTM(random_state=RANDOM_SEED),
        'Meta': LogisticRegression(random_state=RANDOM_SEED)
    }

def split_data(df):
    df = df.sort_values('timestamp').reset_index(drop=True)
    n = len(df)
    train_end = int(n * CHRONO_TRAIN_FRAC)
    val_end = int(n * (CHRONO_TRAIN_FRAC + CHRONO_VAL_FRAC))
    splits = {}
    chrono_train = df.iloc[:train_end]
    chrono_val = df.iloc[train_end:val_end]
    chrono_test = df.iloc[val_end:]
    splits['chronological'] = {'train': chrono_train, 'val': chrono_val, 'test': chrono_test}
    os.makedirs("outputs/datasets", exist_ok=True)
    chrono_test.to_csv("outputs/datasets/chronological_test_set.csv", index=False)
    gss = GroupShuffleSplit(n_splits=1, train_size=GROUP_TRAIN_FRAC, random_state=RANDOM_SEED)
    train_idx, test_idx = next(gss.split(df, groups=df['user_id']))
    gss_val = GroupShuffleSplit(n_splits=1, train_size=GROUP_VAL_FRAC, random_state=RANDOM_SEED)
    train_df = df.iloc[train_idx].reset_index(drop=True)
    t_idx, v_idx = next(gss_val.split(train_df, groups=train_df['user_id']))
    splits['group'] = {'train': train_df.iloc[t_idx], 'val': train_df.iloc[v_idx], 'test': df.iloc[test_idx]}
    df_shuffled = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
    train_df_shuffled, test_df_shuffled = train_test_split(df_shuffled, test_size=1-RANDOM_TRAIN_FRAC, random_state=RANDOM_SEED, stratify=df_shuffled['label'])
    train_df_shuffled, val_df_shuffled = train_test_split(train_df_shuffled, test_size=RANDOM_VAL_FRAC, random_state=RANDOM_SEED, stratify=train_df_shuffled['label'])
    splits['random'] = {'train': train_df_shuffled, 'val': val_df_shuffled, 'test': test_df_shuffled}
    splits['shift'] = {
        'train': df.iloc[:int(n*SHIFT_TRAIN_FRAC)],
        'val': df.iloc[int(n*SHIFT_TRAIN_FRAC):int(n*SHIFT_VAL_FRAC)],
        'test': df.iloc[int(n*SHIFT_TEST_FRAC):]
    }
    return splits

def evaluate_model(model, X_train, y_train, X_test, y_test, apply_smote=True):
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    if apply_smote and y_train.sum() > 5:
        smote = SMOTE(random_state=RANDOM_SEED)
        try:
            X_train_s, y_train = smote.fit_resample(X_train_s, y_train)
        except:
            pass

    model.fit(X_train_s, y_train)
    probs = model.predict_proba(X_test_s)[:, 1]
    preds = model.predict(X_test_s)

    return probs, preds

def run_ablation(df, splits):
    results = []
    # Store predictions for significance testing
    predictions_store = {}

    model = XGBClassifier(random_state=RANDOM_SEED, eval_metric='logloss')

    for variant, features in FEATURE_GROUPS.items():
        predictions_store[variant] = {}
        for split_name, split_dict in splits.items():
            train = split_dict['train']
            test = split_dict['test']

            if test['label'].sum() == 0 or train['label'].sum() == 0:
                pr_auc, f1 = 0.0, 0.0
                predictions_store[variant][split_name] = np.zeros(len(test))
            else:
                probs, preds = evaluate_model(model, train[features], train['label'], test[features], test['label'], apply_smote=False)
                pr_auc = average_precision_score(test['label'], probs)
                f1 = f1_score(test['label'], preds)
                predictions_store[variant][split_name] = probs

            results.append({
                'Variant': variant,
                'Split': split_name,
                'PR-AUC': pr_auc,
                'F1': f1
            })

    df_results = pd.DataFrame(results)
    return df_results, predictions_store

def run_models(df, splits):
    results = []
    cm_results = []
    cv_results = []
    models = get_models()
    features = FEATURE_GROUPS['D_all']

    for split_name in ['chronological', 'group']:
        split_dict = splits[split_name]
        train = split_dict['train']
        test = split_dict['test']

        X_train = train[features]
        y_train = train['label']
        X_test = test[features]
        y_test = test['label']

        meta_train_preds = []
        meta_test_preds = []

        for name, model in models.items():
            if name == 'Meta': continue

            probs, preds = evaluate_model(model, X_train, y_train, X_test, y_test, apply_smote=True)

            # Confusion Matrix
            cm = confusion_matrix(y_test, preds)
            if cm.shape == (2, 2):
                tn, fp, fn, tp = cm.ravel()
            else:
                tn, fp, fn, tp = 0, 0, 0, 0

            cm_results.append({'Model': name, 'Split': split_name, 'TN': tn, 'FP': fp, 'FN': fn, 'TP': tp})

            results.append({
                'Model': name,
                'Split': split_name,
                'PR-AUC': average_precision_score(y_test, probs) if len(np.unique(y_test))>1 else 0,
                'F1': f1_score(y_test, preds) if len(np.unique(y_test))>1 else 0,
                'Recall': recall_score(y_test, preds) if len(np.unique(y_test))>1 else 0
            })

            # Cross Validation metrics for 'group' split
            if split_name == 'group':
                skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
                scores = []
                for train_idx, val_idx in skf.split(X_train, y_train):
                    X_cv_train, X_cv_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
                    y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
                    p, _ = evaluate_model(model, X_cv_train, y_cv_train, X_cv_val, y_cv_val, apply_smote=True)
                    if len(np.unique(y_cv_val)) > 1:
                        scores.append(average_precision_score(y_cv_val, p))
                cv_results.append({'Model': name, 'Mean_CV_PRAUC': np.mean(scores) if scores else 0, 'Std_CV_PRAUC': np.std(scores) if scores else 0})

            scaler = StandardScaler()
            model.fit(scaler.fit_transform(X_train), y_train)
            meta_train_preds.append(model.predict_proba(scaler.transform(X_train))[:, 1])
            meta_test_preds.append(model.predict_proba(scaler.transform(X_test))[:, 1])

        # Meta model
        X_meta_train = np.column_stack(meta_train_preds)
        X_meta_test = np.column_stack(meta_test_preds)
        meta = models['Meta']
        meta.fit(X_meta_train, y_train)
        probs = meta.predict_proba(X_meta_test)[:, 1]
        preds = meta.predict(X_meta_test)

        cm = confusion_matrix(y_test, preds)
        if cm.shape == (2, 2): tn, fp, fn, tp = cm.ravel()
        else: tn, fp, fn, tp = 0, 0, 0, 0
        cm_results.append({'Model': 'Meta', 'Split': split_name, 'TN': tn, 'FP': fp, 'FN': fn, 'TP': tp})

        results.append({
            'Model': 'Meta',
            'Split': split_name,
            'PR-AUC': average_precision_score(y_test, probs) if len(np.unique(y_test))>1 else 0,
            'F1': f1_score(y_test, preds) if len(np.unique(y_test))>1 else 0,
            'Recall': recall_score(y_test, preds) if len(np.unique(y_test))>1 else 0
        })

    return pd.DataFrame(results), pd.DataFrame(cm_results), pd.DataFrame(cv_results)

def calculate_significance(predictions_store):
    comparisons = []

    # 1. A_temporal vs D_all (Chronological)
    preds_A = predictions_store['A_temporal']['chronological']
    preds_D = predictions_store['D_all']['chronological']

    t_stat, p_val = stats.ttest_ind(preds_A, preds_D)
    # Cohen's d
    s_pooled = np.sqrt(((len(preds_A)-1)*np.var(preds_A) + (len(preds_D)-1)*np.var(preds_D)) / (len(preds_A)+len(preds_D)-2))
    d = (np.mean(preds_A) - np.mean(preds_D)) / s_pooled

    comparisons.append({
        'Comparison': 'A_temporal vs D_all (Chronological)',
        'p_value': p_val,
        'cohens_d': d,
        'Significant': p_val < 0.05
    })

    # 2. Chronological vs Group Split (D_all)
    preds_chrono = predictions_store['D_all']['chronological']
    preds_group = predictions_store['D_all']['group']

    t_stat, p_val = stats.ttest_ind(preds_chrono, preds_group)
    s_pooled = np.sqrt(((len(preds_chrono)-1)*np.var(preds_chrono) + (len(preds_group)-1)*np.var(preds_group)) / (len(preds_chrono)+len(preds_group)-2))
    d = (np.mean(preds_chrono) - np.mean(preds_group)) / s_pooled

    comparisons.append({
        'Comparison': 'Chronological vs Group Split (D_all XGBoost)',
        'p_value': p_val,
        'cohens_d': d,
        'Significant': p_val < 0.05
    })

    return pd.DataFrame(comparisons)

if __name__ == "__main__":
    from phase1_ingestion import ingest_data
    from phase2_features import engineer_features
    import os

    df = ingest_data()
    df = engineer_features(df)
    splits = split_data(df)

    ablation_res, preds_store = run_ablation(df, splits)
    ablation_res.to_csv("outputs/tables/ablation_study.csv", index=False)

    model_res, cm_res, cv_res = run_models(df, splits)
    model_res.to_csv("outputs/tables/model_evaluations.csv", index=False)
    cm_res.to_csv("outputs/tables/confusion_matrices.csv", index=False)
    cv_res.to_csv("outputs/tables/cross_validation.csv", index=False)

    sig_res = calculate_significance(preds_store)
    sig_res.to_csv("outputs/tables/significance_tests.csv", index=False)
