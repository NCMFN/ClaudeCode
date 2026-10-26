import pandas as pd
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import OrdinalEncoder
from typing import Dict, List, Tuple
import logging
import os
import csv
import copy

logger = logging.getLogger(__name__)

def evaluate_predictions(df_test: pd.DataFrame, y_true: pd.Series, y_score: np.ndarray, true_prevalence: float, df_train: pd.DataFrame = None) -> Dict[str, float]:
    if y_true.sum() == 0:
        return {'pr_auc': np.nan, 'roc_auc': np.nan, 'recall_1_alert': np.nan,
                'recall_10_alerts': np.nan, 'recall_100_alerts': np.nan,
                'precision_at_k': np.nan, 'days_to_first_detect': np.nan,
                'prevalence_baseline': true_prevalence}

    try:
        pr_auc = average_precision_score(y_true, y_score)
        roc_auc = roc_auc_score(y_true, y_score)
    except Exception as e:
        pr_auc = np.nan
        roc_auc = np.nan

    metrics = {
        'pr_auc': pr_auc,
        'roc_auc': roc_auc,
        'prevalence_baseline': true_prevalence
    }

    num_days = df_test['day'].nunique()
    if num_days > 0:
        budget_1 = int(1 * num_days)
        budget_10 = int(10 * num_days)
        budget_100 = int(100 * num_days)

        sorted_indices = np.argsort(-y_score)

        def recall_at_budget(budget):
            if budget == 0: return 0
            k = min(budget, len(y_true))
            top_k_indices = sorted_indices[:k]
            true_positives = y_true.iloc[top_k_indices].sum()
            return true_positives / y_true.sum()

        metrics['recall_1_alert'] = recall_at_budget(budget_1)
        metrics['recall_10_alerts'] = recall_at_budget(budget_10)
        metrics['recall_100_alerts'] = recall_at_budget(budget_100)

        k = int(y_true.sum())
        top_k_indices = sorted_indices[:k]
        metrics['precision_at_k'] = y_true.iloc[top_k_indices].sum() / k if k > 0 else np.nan

    if num_days > 0:
        threshold_idx = min(int(10 * num_days), len(y_score) - 1)
        threshold = np.sort(y_score)[::-1][threshold_idx]

        alerts = df_test[y_score >= threshold]
        malicious_alerts = alerts[alerts['is_malicious'] == 1]

        if not malicious_alerts.empty:
            first_detect_time = malicious_alerts['time'].min()
            if df_train is not None and not df_train.empty:
                start_time = df_train['time'].max()
            else:
                start_time = df_test['time'].min()

            days_to_first = (first_detect_time - start_time) / 86400
            metrics['days_to_first_detect'] = max(0, days_to_first)
        else:
            metrics['days_to_first_detect'] = np.nan

    return metrics

def compute_paired_delta_ci(y_true: pd.Series, y_score_base: pd.Series, y_score_comp: pd.Series, group_ids: pd.Series, n_bootstraps: int = 100) -> Tuple[float, float]:
    groups = group_ids.unique()
    n_groups = len(groups)
    deltas = []

    df = pd.DataFrame({
        'y_true': y_true.values,
        'y_base': y_score_base.values,
        'y_comp': y_score_comp.values,
        'group': group_ids.values
    })

    for i in range(n_bootstraps):
        boot_groups = np.random.choice(groups, size=n_groups, replace=True)
        boot_df = pd.concat([df[df['group'] == g] for g in boot_groups])

        if boot_df['y_true'].sum() > 0:
            try:
                score_base = average_precision_score(boot_df['y_true'], boot_df['y_base'])
                score_comp = average_precision_score(boot_df['y_true'], boot_df['y_comp'])
                deltas.append(score_base - score_comp)
            except Exception:
                pass

    if not deltas:
        return np.nan, np.nan

    return np.percentile(deltas, 2.5), np.percentile(deltas, 97.5)


def run_evaluation_protocol(df: pd.DataFrame, feature_cols: List[str], model_name: str, model_obj, protocol_generator, protocol_name: str, true_prevalence: float, df_groups: pd.Series = None) -> Tuple[List[Dict], List[object]]:
    results = []
    trained_models = []

    time_features = ['hour_sin', 'hour_cos', 'day_of_week']
    non_time_features = [f for f in feature_cols if f not in time_features]

    cat_cols = ['auth_type', 'logon_type', 'auth_orientation', 'success']

    for fold_idx, (train_idx, test_idx) in enumerate(protocol_generator):
        if len(train_idx) == 0 or len(test_idx) == 0:
            continue

        df_train = df.iloc[train_idx].copy()
        df_test = df.iloc[test_idx].copy()

        y_train = df_train['is_malicious']
        y_test = df_test['is_malicious']

        if y_train.sum() == 0 or y_test.sum() == 0:
             results.append({'fold': fold_idx, 'model': model_name, 'protocol': protocol_name, 'pr_auc': 'NA', 'status': 'INCONCLUSIVE'})
             continue

        # Fit encoder on train, apply to train and test safely
        enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
        valid_cats = [c for c in cat_cols if c in df_train.columns]
        if valid_cats:
            enc.fit(df_train[valid_cats])

            # Map encoded features to columns expected by feature_cols
            train_enc = enc.transform(df_train[valid_cats])
            test_enc = enc.transform(df_test[valid_cats])

            for i, c in enumerate(valid_cats):
                df_train[f'{c}_encoded'] = train_enc[:, i]
                df_test[f'{c}_encoded'] = test_enc[:, i]

        X_train, X_test = df_train[feature_cols], df_test[feature_cols]
        m_full, _, trained_mdl = _fit_eval(model_obj, X_train, y_train, X_test, df_test, true_prevalence, df_groups, df_train, model_name, fold_idx, protocol_name, "full")
        results.append(m_full)
        trained_models.append((trained_mdl, enc))

        X_train_time, X_test_time = df_train[time_features], df_test[time_features]
        m_time, _, _ = _fit_eval(model_obj, X_train_time, y_train, X_test_time, df_test, true_prevalence, df_groups, df_train, model_name, fold_idx, protocol_name, "time_only")
        results.append(m_time)

        X_train_notime, X_test_notime = df_train[non_time_features], df_test[non_time_features]
        m_notime, _, _ = _fit_eval(model_obj, X_train_notime, y_train, X_test_notime, df_test, true_prevalence, df_groups, df_train, model_name, fold_idx, protocol_name, "ablation_no_time")
        results.append(m_notime)

        y_train_shuffled = y_train.sample(frac=1, random_state=42).reset_index(drop=True)
        m_shuff, _, _ = _fit_eval(model_obj, X_train, y_train_shuffled, X_test, df_test, true_prevalence, df_groups, df_train, model_name, fold_idx, protocol_name, "label_shuffle")
        results.append(m_shuff)

    return results, trained_models

def _fit_eval(base_model_obj, X_train, y_train, X_test, df_test, true_prevalence, df_groups, df_train, model_name, fold_idx, protocol_name, probe_type):
    from sklearn.base import clone
    model_obj = clone(base_model_obj)
    y_test = df_test['is_malicious']
    try:
        model_obj.fit(X_train, y_train)
        if hasattr(model_obj, "predict_proba"):
            y_score = model_obj.predict_proba(X_test)[:, 1]
        else:
            y_score = -model_obj.score_samples(X_test)

        metrics = evaluate_predictions(df_test, y_test, y_score, true_prevalence, df_train)

        metrics.update({
            'fold': fold_idx,
            'model': model_name,
            'protocol': protocol_name,
            'probe_type': probe_type,
            'status': 'COMPLETED'
        })
        return metrics, pd.Series(y_score, index=y_test.index), model_obj
    except Exception as e:
        logger.error(f"Error evaluating {model_name} ({probe_type}) on fold {fold_idx}: {e}")
        return {'fold': fold_idx, 'model': model_name, 'protocol': protocol_name, 'probe_type': probe_type, 'pr_auc': 'NA', 'status': 'FAILED'}, None, None

def evaluate_paired_deltas(df: pd.DataFrame, feature_cols: List[str], df_groups: pd.Series, p3_generator, trained_models: Dict[str, Dict[str, List]]):
    os.makedirs('outputs/tables', exist_ok=True)
    with open('outputs/tables/leakage_delta.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['model', 'comparison', 'base_pr_auc', 'comp_pr_auc', 'delta_pr_auc', 'ci_low', 'ci_high'])

        folds = list(p3_generator)
        if not folds: return

        train_idx, test_idx = folds[0]
        if len(test_idx) == 0: return

        df_test = df.iloc[test_idx].copy()
        y_test = df_test['is_malicious']
        group_ids = df_test[df_groups.name] if df_groups is not None else pd.Series([1]*len(df_test))

        if y_test.sum() == 0: return

        cat_cols = ['auth_type', 'logon_type', 'auth_orientation', 'success']

        for model_name, protocols_dict in trained_models.items():
            p3_tup = protocols_dict.get('P3', [(None, None)])[0]
            p1_tup = protocols_dict.get('P1', [(None, None)])[0]
            p2_tup = protocols_dict.get('P2', [(None, None)])[0]

            p3_model, p3_enc = p3_tup if p3_tup else (None, None)

            if p3_model is None: continue

            # encode test set according to p3 enc
            df_test_p3 = df_test.copy()
            valid_cats = [c for c in cat_cols if c in df_test_p3.columns]
            if valid_cats and p3_enc:
                test_enc = p3_enc.transform(df_test_p3[valid_cats])
                for i, c in enumerate(valid_cats): df_test_p3[f'{c}_encoded'] = test_enc[:, i]

            X_test_p3 = df_test_p3[feature_cols]

            def score(m, X):
                if hasattr(m, "predict_proba"): return m.predict_proba(X)[:, 1]
                return -m.score_samples(X)

            y_score_p3 = pd.Series(score(p3_model, X_test_p3))
            p3_pr_auc = average_precision_score(y_test, y_score_p3)

            for comp_name, comp_tup in [('P1', p1_tup), ('P2', p2_tup)]:
                m_comp, enc_comp = comp_tup if comp_tup else (None, None)
                if m_comp is not None:
                    df_test_comp = df_test.copy()
                    if valid_cats and enc_comp:
                        test_enc = enc_comp.transform(df_test_comp[valid_cats])
                        for i, c in enumerate(valid_cats): df_test_comp[f'{c}_encoded'] = test_enc[:, i]
                    X_test_comp = df_test_comp[feature_cols]

                    y_score_comp = pd.Series(score(m_comp, X_test_comp))
                    comp_pr_auc = average_precision_score(y_test, y_score_comp)
                    delta = comp_pr_auc - p3_pr_auc
                    ci_low, ci_high = compute_paired_delta_ci(y_test, y_score_comp, y_score_p3, group_ids)
                    writer.writerow([model_name, f'{comp_name}-vs-P3', p3_pr_auc, comp_pr_auc, delta, ci_low, ci_high])
