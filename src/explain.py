import os
import csv
import numpy as np
import pandas as pd
import shap
from xgboost import XGBClassifier
from features import build_features, extract_X_y
from config import SEED

def run_explainability(df, folds):
    os.makedirs("outputs/tables", exist_ok=True)
    os.makedirs("outputs/datasets", exist_ok=True) # for saving shap objects

    tr, te = folds[0]
    f_df, f_cols = build_features(df, train_idx=tr, use_temporal=True)
    X_tr, _, y_tr = extract_X_y(f_df.iloc[tr], f_cols)

    # Stratified, seeded sample of test fold
    te_df = f_df.iloc[te]
    pos_te = te_df[te_df['label'] == 1]
    neg_te = te_df[te_df['label'] == 0]

    # 50 positives, 150 negatives if available
    np.random.seed(SEED)
    pos_samp = pos_te.sample(min(len(pos_te), 50), random_state=SEED) if not pos_te.empty else pos_te
    neg_samp = neg_te.sample(min(len(neg_te), 150), random_state=SEED) if not neg_te.empty else neg_te

    te_samp = pd.concat([pos_samp, neg_samp])
    if te_samp.empty:
        return

    X_te_samp, _, _ = extract_X_y(te_samp, f_cols)

    if len(np.unique(y_tr)) > 1:
        clf = XGBClassifier(random_state=SEED, eval_metric='logloss')
        clf.fit(X_tr, y_tr)

        explainer = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(X_te_samp)

        mean_abs_shap = np.abs(shap_values).mean(axis=0)

        with open("outputs/tables/shap_mean_abs.csv", "w", newline='') as f:
            w = csv.writer(f)
            w.writerow(["feature", "mean_abs_shap"])
            for col, val in zip(f_cols, mean_abs_shap):
                w.writerow([col, val])

        # save arrays for plotting
        np.save("outputs/datasets/shap_values.npy", shap_values)
        np.save("outputs/datasets/shap_X.npy", X_te_samp)
        with open("outputs/datasets/shap_cols.json", "w") as f:
            import json
            json.dump(f_cols, f)

    else:
        with open("outputs/tables/shap_mean_abs.csv", "w", newline='') as f:
            w = csv.writer(f)
            w.writerow(["feature", "mean_abs_shap"])
            for col in f_cols:
                w.writerow([col, 0.0])
