import os
import csv
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score
from features import build_features, extract_X_y
from models import train_base_models, train_negative_controls
from config import SEED

def compute_pr_auc(y_true, y_pred):
    if len(np.unique(y_true)) < 2:
        return 0.0
    return average_precision_score(y_true, y_pred)

def bootstrap_pr_auc(y_true, y_pred, user_groups, n_bootstrap=100):
    np.random.seed(SEED)
    users = np.unique(user_groups)
    scores = []

    if len(np.unique(y_true)) < 2:
        return 0.0, 0.0, 0.0

    for _ in range(n_bootstrap):
        sample_users = np.random.choice(users, size=len(users), replace=True)
        # build indices
        idx = []
        for u in sample_users:
            idx.extend(np.where(user_groups == u)[0])

        y_t = y_true[idx]
        y_p = y_pred[idx]

        if len(np.unique(y_t)) > 1:
            scores.append(average_precision_score(y_t, y_p))

    if not scores:
        return 0.0, 0.0, 0.0
    scores = np.array(scores)
    return np.mean(scores), np.percentile(scores, 2.5), np.percentile(scores, 97.5)

def run_leakage_audit(df, splits):
    """
    Arms:
    1. Leaky sampling (replicates bug) -> we will synthesize this by creating a leaky DF
    2. Matched sampling (the real df)
    3. Time-only negative control
    4. Label-shuffle control
    5. Split-strategy sweep
    """
    os.makedirs("outputs/tables", exist_ok=True)

    # We will use XGBoost as the probe model for the audit

    # -- Arm 1: Leaky sampling --
    # To replicate the bug: benign rows from early time, malicious rows at their real time
    pos_df = df[df['label'] == 1].copy()
    neg_df = df[df['label'] == 0].copy().sort_values('time').head(max(len(pos_df)*10, 1000))
    leaky_df = pd.concat([pos_df, neg_df]).sort_values('time').reset_index(drop=True)

    leaky_feat, feature_cols = build_features(leaky_df, use_temporal=True)
    # Train-test split 80-20 random
    np.random.seed(SEED)
    idx = np.random.permutation(len(leaky_feat))
    split_pt = int(0.8 * len(idx))
    tr_idx, te_idx = idx[:split_pt], idx[split_pt:]

    X_tr, _, y_tr = extract_X_y(leaky_feat.iloc[tr_idx], feature_cols)
    X_te, _, y_te = extract_X_y(leaky_feat.iloc[te_idx], feature_cols)

    from xgboost import XGBClassifier
    clf_leaky = XGBClassifier(random_state=SEED, eval_metric='logloss')
    if len(np.unique(y_tr)) > 1:
        clf_leaky.fit(X_tr, y_tr)
        preds_leaky = clf_leaky.predict_proba(X_te)[:, 1]
        leaky_prauc = compute_pr_auc(y_te, preds_leaky)
    else:
        leaky_prauc = 0.0

    # -- Arm 2: Matched sampling --
    # We use chronological split fold 0
    tr_idx, te_idx = splits['chronological_holdout'][0]
    matched_feat, _ = build_features(df, train_idx=tr_idx, use_temporal=True)
    X_tr, _, y_tr = extract_X_y(matched_feat.iloc[tr_idx], feature_cols)
    X_te, _, y_te = extract_X_y(matched_feat.iloc[te_idx], feature_cols)

    clf_matched = XGBClassifier(random_state=SEED, eval_metric='logloss')
    if len(np.unique(y_tr)) > 1:
        clf_matched.fit(X_tr, y_tr)
        preds_matched = clf_matched.predict_proba(X_te)[:, 1]
        matched_prauc = compute_pr_auc(y_te, preds_matched)
    else:
        matched_prauc = 0.0

    with open("outputs/tables/leakage_audit_arms.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["arm", "pr_auc"])
        w.writerow(["Leaky Sampling (Bug Replication)", leaky_prauc])
        w.writerow(["Matched Sampling (Chronological)", matched_prauc])

    # -- Arm 3: Time-only & Label Shuffle --
    time_cols = ['hour_cos', 'hour_sin']
    X_tr_time = matched_feat.iloc[tr_idx][time_cols].values
    X_te_time = matched_feat.iloc[te_idx][time_cols].values

    y_tr_shuf = y_tr.copy()
    np.random.seed(SEED)
    np.random.shuffle(y_tr_shuf)

    t_model, s_model = train_negative_controls(X_tr_time, y_tr, X_tr, y_tr_shuf)

    if len(np.unique(y_tr)) > 1:
        preds_time = t_model.predict_proba(X_te_time)[:, 1]
        time_prauc = compute_pr_auc(y_te, preds_time)
        preds_shuf = s_model.predict_proba(X_te)[:, 1]
        shuf_prauc = compute_pr_auc(y_te, preds_shuf)
    else:
        time_prauc = 0.0
        shuf_prauc = 0.0

    prevalence = np.mean(y_te) if len(y_te) > 0 else 0.0

    with open("outputs/tables/time_only_control.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["control", "pr_auc", "prevalence"])
        w.writerow(["Time-only features", time_prauc, prevalence])

    with open("outputs/tables/label_shuffle_control.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["control", "pr_auc", "prevalence"])
        w.writerow(["Label-shuffle", shuf_prauc, prevalence])

    # -- Arm 4: Split-strategy sweep --
    with open("outputs/tables/leakage_gap_by_split.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["strategy", "pr_auc_mean", "pr_auc_lower", "pr_auc_upper"])

        for strategy, folds in splits.items():
            if not folds:
                continue
            tr, te = folds[0]
            if len(tr) == 0 or len(te) == 0:
                continue
            f_df, _ = build_features(df, train_idx=tr, use_temporal=True)
            Xt, _, yt = extract_X_y(f_df.iloc[tr], feature_cols)
            Xv, _, yv = extract_X_y(f_df.iloc[te], feature_cols)

            if len(np.unique(yt)) > 1:
                clf = XGBClassifier(random_state=SEED, eval_metric='logloss')
                clf.fit(Xt, yt)
                pv = clf.predict_proba(Xv)[:, 1]

                mean_auc, low_auc, high_auc = bootstrap_pr_auc(yv, pv, f_df.iloc[te]['user'].values)
                w.writerow([strategy, mean_auc, low_auc, high_auc])
            else:
                w.writerow([strategy, 0.0, 0.0, 0.0])

    # -- Arm 5: Feature attribution share --
    import shap
    shap_sample = matched_feat.iloc[te_idx].sample(min(200, len(te_idx)), random_state=SEED)
    Xs = shap_sample[feature_cols].values

    if len(np.unique(y_tr)) > 1:
        explainer = shap.TreeExplainer(clf_matched)
        # Fix: catch AdditivityError by passing check_additivity=False if needed,
        # but standard XGBoost should be fine.
        shap_values = explainer.shap_values(Xs)

        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        total_shap = mean_abs_shap.sum()

        time_idx = [feature_cols.index(c) for c in time_cols]
        time_shap = mean_abs_shap[time_idx].sum()

        share = time_shap / total_shap if total_shap > 0 else 0.0
    else:
        share = 0.0

    with open("outputs/tables/attribution_share_temporal.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["feature_group", "share"])
        w.writerow(["temporal", share])
