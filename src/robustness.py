import os
import csv
import numpy as np
from xgboost import XGBClassifier
from features import build_features, extract_X_y
from leakage_audit import compute_pr_auc
from config import SEED

def evasion_perturbation(X, y, feature_cols, clf):
    """
    Perturb features the model actually uses.
    """
    X_pert = X.copy()
    importance = clf.feature_importances_
    top_idx = np.argsort(importance)[::-1][:3]

    # Simple evasion: push top features toward mean of benign class
    benign_X = X[y == 0]
    if len(benign_X) > 0:
        for idx in top_idx:
            mean_benign = benign_X[:, idx].mean()
            # perturb malicious rows
            mal_mask = (y == 1)
            X_pert[mal_mask, idx] = mean_benign

    return X_pert

def run_robustness(df, folds):
    os.makedirs("outputs/tables", exist_ok=True)

    tr, te = folds[0]
    f_df, f_cols = build_features(df, train_idx=tr, use_temporal=True)
    X_tr, _, y_tr = extract_X_y(f_df.iloc[tr], f_cols)
    X_te, _, y_te = extract_X_y(f_df.iloc[te], f_cols)

    res = []

    if len(np.unique(y_tr)) > 1:
        clf = XGBClassifier(random_state=SEED, eval_metric='logloss')
        clf.fit(X_tr, y_tr)

        # Baseline
        base_pr = compute_pr_auc(y_te, clf.predict_proba(X_te)[:, 1])
        res.append(["Baseline", base_pr])

        # Evasion
        X_te_ev = evasion_perturbation(X_te, y_te, f_cols, clf)
        ev_pr = compute_pr_auc(y_te, clf.predict_proba(X_te_ev)[:, 1])
        res.append(["Evasion (Top-3 features pushed to benign mean)", ev_pr])

        # Poisoning
        np.random.seed(SEED)
        y_tr_pois = y_tr.copy()
        flip_idx = np.random.choice(len(y_tr), size=int(0.05 * len(y_tr)), replace=False)
        y_tr_pois[flip_idx] = 1 - y_tr_pois[flip_idx]

        clf_pois = XGBClassifier(random_state=SEED, eval_metric='logloss')
        if len(np.unique(y_tr_pois)) > 1:
            clf_pois.fit(X_tr, y_tr_pois)
            pois_pr = compute_pr_auc(y_te, clf_pois.predict_proba(X_te)[:, 1])
        else:
            pois_pr = 0.0
        res.append(["Poisoning (5% label flip)", pois_pr])

        # Drift: test on a fold much later
        if len(folds) > 1:
            tr_last, te_last = folds[-1]
            f_df_last, _ = build_features(df, train_idx=tr_last, use_temporal=True)
            X_te_last, _, y_te_last = extract_X_y(f_df_last.iloc[te_last], f_cols)
            if len(np.unique(y_te_last)) > 1:
                drift_pr = compute_pr_auc(y_te_last, clf.predict_proba(X_te_last)[:, 1])
            else:
                drift_pr = 0.0
            res.append(["Temporal Drift (Train early, test late)", drift_pr])
        else:
            res.append(["Temporal Drift", 0.0])
    else:
        res.extend([["Baseline", 0.0], ["Evasion", 0.0], ["Poisoning", 0.0], ["Temporal Drift", 0.0]])

    with open("outputs/tables/robustness.csv", "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["stress_test", "pr_auc"])
        for r in res:
            w.writerow(r)
