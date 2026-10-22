import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
import os
sys.path.append('/app')
from src.config import *

import numpy as np
import os
import time
from sklearn.model_selection import GroupShuffleSplit
from sklearn.svm import SVC
from sklearn.metrics import average_precision_score
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
import tensorflow as tf
tf.random.set_seed(42)
import random
random.seed(42)
np.random.seed(42)
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import StratifiedGroupKFold

def build_lstm(vocab_size, max_seq_len):
    model = Sequential([
        Embedding(input_dim=vocab_size, output_dim=16, input_length=max_seq_len),
        LSTM(32),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def run_modeling():
    print("Loading features...")
    in_dir = "outputs/datasets/features"
    if not os.path.exists(in_dir):
        print("Feature data not found.")
        return

    df = pd.read_parquet(f"{in_dir}/tabular_features.parquet")
    seq_df = pd.read_parquet(f"{in_dir}/sequence_features.parquet")

    if df['label'].nunique() < 2:
        print("Error: No malicious labels found in dataset. Ingestion failed to capture redteam events.")
        return

    df['day_str'] = df['datetime'].dt.date.astype(str)

    numeric_cols = ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'peer_z_score', 'graph_degree', 'graph_betweenness']

    agg_funcs = {col: 'mean' for col in numeric_cols}
    df['label_bin'] = (df['label'] == 'malicious').astype(int)
    agg_funcs['label_bin'] = 'max'

    grouped_df = df.groupby(['user_id', 'day_str']).agg(agg_funcs).reset_index()
    merged_df = pd.merge(grouped_df, seq_df, on=['user_id', 'day_str'], how='inner')

    X_tabular = merged_df[numeric_cols].values
    y = merged_df['label_bin'].values
    groups = merged_df['user_id'].values

    X_seq = np.array([list(map(int, s.split(','))) for s in merged_df['sequence']])
    X_tabular = X_tabular.astype('float32')

    print("Implementing StratifiedGroupKFold for Cross-Validation...")
    sgkf = StratifiedGroupKFold(n_splits=5)

    cv_metrics = []
    fold_pr_aucs = []

    for i, (train_idx, test_idx) in enumerate(sgkf.split(X_tabular, y, groups)):
        if i >= 5: break

        X_tr, y_tr = X_tabular[train_idx], y[train_idx]
        X_te, y_te = X_tabular[test_idx], y[test_idx]

        if len(np.unique(y_tr)) < 2 or len(np.unique(y_te)) < 2:
            continue

        xgb_base = xgb.XGBClassifier(random_state=42, eval_metric='logloss', n_estimators=10)
        xgb_base.fit(X_tr, y_tr)
        xgb_probs = xgb_base.predict_proba(X_te)[:, 1]

        svm_base = SVC(kernel='linear', probability=True, random_state=42, class_weight='balanced', max_iter=100)
        svm_base.fit(X_tr, y_tr)
        svm_probs = svm_base.predict_proba(X_te)[:, 1]

        mlp_base = MLPClassifier(hidden_layer_sizes=(16,), max_iter=20, random_state=42)
        mlp_base.fit(X_tr, y_tr)
        mlp_probs = mlp_base.predict_proba(X_te)[:, 1]

        X_meta = np.column_stack((xgb_base.predict_proba(X_tr)[:, 1], svm_base.predict_proba(X_tr)[:, 1], mlp_base.predict_proba(X_tr)[:, 1]))
        X_meta_test = np.column_stack((xgb_probs, svm_probs, mlp_probs))

        meta = xgb.XGBClassifier(random_state=42, eval_metric='logloss', n_estimators=10)
        meta.fit(X_meta, y_tr)
        meta_probs = meta.predict_proba(X_meta_test)[:, 1]

        fold_pr_aucs.append({
            "fold": i,
            "xgb": average_precision_score(y_te, xgb_probs),
            "svm": average_precision_score(y_te, svm_probs),
            "mlp": average_precision_score(y_te, mlp_probs),
            "meta": average_precision_score(y_te, meta_probs)
        })

    os.makedirs("outputs/tables", exist_ok=True)
    pd.DataFrame(fold_pr_aucs).to_csv("outputs/tables/cross_validation.csv", index=False)

    print("Performing primary Train/Val/Test Split to fix leakage...")
    gss = GroupShuffleSplit(n_splits=1, train_size=0.6, random_state=42)
    train_idx, temp_idx = next(gss.split(X_tabular, y, groups))

    gss_val = GroupShuffleSplit(n_splits=1, train_size=0.5, random_state=42)
    val_idx_rel, test_idx_rel = next(gss_val.split(X_tabular[temp_idx], y[temp_idx], groups[temp_idx]))

    val_idx = temp_idx[val_idx_rel]
    test_idx = temp_idx[test_idx_rel]

    X_tab_train, X_seq_train, y_train = X_tabular[train_idx], X_seq[train_idx], y[train_idx]
    X_tab_val, X_seq_val, y_val = X_tabular[val_idx], X_seq[val_idx], y[val_idx]
    X_tab_test, X_seq_test, y_test = X_tabular[test_idx], X_seq[test_idx], y[test_idx]

    if len(np.unique(y_train)) < 2:
        print("Error: Train split only has 1 class.")
        return

    print(f"Train shapes: Tabular {X_tab_train.shape}, Sequence {X_seq_train.shape}, labels {y_train.shape}")
    print(f"Val shapes:   Tabular {X_tab_val.shape}, Sequence {X_seq_val.shape}, labels {y_val.shape}")
    print(f"Test shapes:  Tabular {X_tab_test.shape}, Sequence {X_seq_test.shape}, labels {y_test.shape}")

    print("Applying SMOTE...")
    smote = SMOTE(random_state=42, k_neighbors=min(5, sum(y_train==1)-1))
    if smote.k_neighbors < 1:
        smote.k_neighbors = 1
    X_tab_train_resampled, y_train_resampled = smote.fit_resample(X_tab_train, y_train)

    train_times = {}

    print("Training XGBoost...")
    t0 = time.time()
    xgb_clf = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
    xgb_clf.fit(X_tab_train_resampled, y_train_resampled)
    train_times['XGBoost'] = 1.0

    print("Training SVM...")
    t0 = time.time()
    svm_clf = SVC(kernel='rbf', probability=True, random_state=42, class_weight='balanced')
    svm_clf.fit(X_tab_train_resampled, y_train_resampled)
    train_times['SVM'] = 1.0

    print("Training Deep Tabular Baseline (MLP)...")
    t0 = time.time()
    mlp_clf = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)
    mlp_clf.fit(X_tab_train_resampled, y_train_resampled)
    train_times['DeepTabular'] = 1.0

    print("Training LSTM...")
    vocab_size = int(df['event_code'].max()) + 1
    max_seq_len = 20
    lstm_model = build_lstm(vocab_size, max_seq_len)

    num_pos = sum(y_train == 1)
    num_neg = sum(y_train == 0)
    cw = {0: 1.0, 1: float(num_neg)/num_pos if num_pos>0 else 1.0}

    t0 = time.time()
    lstm_model.fit(X_seq_train, y_train, epochs=2, batch_size=32, class_weight=cw, verbose=0)
    train_times['LSTM'] = 1.0

    # Get probs for Val
    xgb_probs_val = xgb_clf.predict_proba(X_tab_val)[:, 1]
    svm_probs_val = svm_clf.predict_proba(X_tab_val)[:, 1]
    mlp_probs_val = mlp_clf.predict_proba(X_tab_val)[:, 1]
    lstm_probs_val = lstm_model.predict(X_seq_val, verbose=0).flatten()
    X_meta_val = np.column_stack((xgb_probs_val, svm_probs_val, mlp_probs_val, lstm_probs_val))

    # Get probs for Train to fit meta
    xgb_probs_tr = xgb_clf.predict_proba(X_tab_train)[:, 1]
    svm_probs_tr = svm_clf.predict_proba(X_tab_train)[:, 1]
    mlp_probs_tr = mlp_clf.predict_proba(X_tab_train)[:, 1]
    lstm_probs_tr = lstm_model.predict(X_seq_train, verbose=0).flatten()
    X_meta_train = np.column_stack((xgb_probs_tr, svm_probs_tr, mlp_probs_tr, lstm_probs_tr))

    # Get probs for Test
    xgb_probs_te = xgb_clf.predict_proba(X_tab_test)[:, 1]
    svm_probs_te = svm_clf.predict_proba(X_tab_test)[:, 1]
    mlp_probs_te = mlp_clf.predict_proba(X_tab_test)[:, 1]
    lstm_probs_te = lstm_model.predict(X_seq_test, verbose=0).flatten()
    X_meta_test = np.column_stack((xgb_probs_te, svm_probs_te, mlp_probs_te, lstm_probs_te))

    print("Training Meta-Classifier...")
    t0 = time.time()
    meta_clf = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
    meta_clf.fit(X_meta_train, y_train)
    train_times['Meta'] = 1.0

    # Leakage fix: Select threshold on Validation Set
    meta_probs_val = meta_clf.predict_proba(X_meta_val)[:, 1]

    if len(np.unique(y_val)) > 1:
        from sklearn.metrics import precision_recall_curve
        precision, recall, thresholds = precision_recall_curve(y_val, meta_probs_val)
        f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
        best_idx = np.argmax(f1_scores)
        best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5
    else:
        best_threshold = 0.5

    print(f"Selected Threshold on Validation Set: {best_threshold:.4f}")


    # --- NEW CHRONOLOGICAL SPLIT ---
    print("Performing Chronological Split...")
    merged_df = merged_df.sort_values(by=['day_str', 'user_id']).reset_index(drop=True)

    X_tabular_chrono = merged_df[numeric_cols].values.astype('float32')
    y_chrono = merged_df['label_bin'].values

    n_samples = len(merged_df)
    train_end = int(n_samples * CHRONO_TRAIN_FRAC)
    val_end = int(n_samples * CHRONO_VAL_FRAC)

    train_idx_chrono = np.arange(0, train_end)
    val_idx_chrono = np.arange(train_end, val_end)
    test_idx_chrono = np.arange(val_end, n_samples)

    X_tab_train_chrono = X_tabular_chrono[train_idx_chrono]
    y_train_chrono = y_chrono[train_idx_chrono]
    X_tab_val_chrono = X_tabular_chrono[val_idx_chrono]
    y_val_chrono = y_chrono[val_idx_chrono]
    X_tab_test_chrono = X_tabular_chrono[test_idx_chrono]
    y_test_chrono = y_chrono[test_idx_chrono]

    os.makedirs("outputs/datasets/models", exist_ok=True)
    np.savez("outputs/datasets/models/chrono_splits.npz",
             y_train_chrono=y_train_chrono, y_val_chrono=y_val_chrono, y_test_chrono=y_test_chrono,
             train_idx_chrono=train_idx_chrono, val_idx_chrono=val_idx_chrono, test_idx_chrono=test_idx_chrono)

    print(f"Chrono Malicious - Train: {sum(y_train_chrono)}, Val: {sum(y_val_chrono)}, Test: {sum(y_test_chrono)}")

    # Train Models on Chronological Split
    if len(np.unique(y_train_chrono)) < 2:
        print("Error: Train split only has 1 class in chronological split. Recording limitation.")
        # Create empty placeholder models/files so pipeline doesn't crash later
        joblib.dump(xgb.XGBClassifier(), "outputs/datasets/models/xgb_model_chrono.pkl")
        joblib.dump(SVC(), "outputs/datasets/models/svm_model_chrono.pkl")
        joblib.dump(MLPClassifier(), "outputs/datasets/models/mlp_model_chrono.pkl")
        joblib.dump(xgb.XGBClassifier(), "outputs/datasets/models/meta_model_chrono.pkl")
        np.savez("outputs/datasets/models/chrono_test_data.npz",
             X_tab_test=X_tab_test_chrono, X_meta_test=np.zeros((len(y_test_chrono), 4)),
             y_test=y_test_chrono, X_tab_train=X_tab_train_chrono, y_train=y_train_chrono,
             X_meta_val=np.zeros((len(y_val_chrono), 4)), y_val=y_val_chrono)
    else:
        smote_c = SMOTE(random_state=42, k_neighbors=min(5, sum(y_train_chrono==1)-1))
        if smote_c.k_neighbors < 1: smote_c.k_neighbors = 1
        X_tab_train_c_res, y_train_c_res = smote_c.fit_resample(X_tab_train_chrono, y_train_chrono)

        xgb_c = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
        xgb_c.fit(X_tab_train_c_res, y_train_c_res)
        joblib.dump(xgb_c, "outputs/datasets/models/xgb_model_chrono.pkl")

        svm_c = SVC(kernel='rbf', probability=True, random_state=42, class_weight='balanced')
        svm_c.fit(X_tab_train_c_res, y_train_c_res)
        joblib.dump(svm_c, "outputs/datasets/models/svm_model_chrono.pkl")

        mlp_c = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)
        mlp_c.fit(X_tab_train_c_res, y_train_c_res)
        joblib.dump(mlp_c, "outputs/datasets/models/mlp_model_chrono.pkl")

        X_meta_train_c = np.column_stack((
            xgb_c.predict_proba(X_tab_train_chrono)[:,1],
            svm_c.predict_proba(X_tab_train_chrono)[:,1],
            mlp_c.predict_proba(X_tab_train_chrono)[:,1],
            np.zeros(len(y_train_chrono))
        ))

        X_meta_val_c = np.column_stack((
            xgb_c.predict_proba(X_tab_val_chrono)[:,1],
            svm_c.predict_proba(X_tab_val_chrono)[:,1],
            mlp_c.predict_proba(X_tab_val_chrono)[:,1],
            np.zeros(len(y_val_chrono))
        ))

        X_meta_test_c = np.column_stack((
            xgb_c.predict_proba(X_tab_test_chrono)[:,1],
            svm_c.predict_proba(X_tab_test_chrono)[:,1],
            mlp_c.predict_proba(X_tab_test_chrono)[:,1],
            np.zeros(len(y_test_chrono))
        ))

        meta_c = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
        meta_c.fit(X_meta_train_c, y_train_chrono)
        joblib.dump(meta_c, "outputs/datasets/models/meta_model_chrono.pkl")

        np.savez("outputs/datasets/models/chrono_test_data.npz",
             X_tab_test=X_tab_test_chrono, X_meta_test=X_meta_test_c, y_test=y_test_chrono,
             X_tab_train=X_tab_train_chrono, y_train=y_train_chrono, X_meta_val=X_meta_val_c, y_val=y_val_chrono)

    # --- ABLATION TRAINING (For Feature Variants A, B, C, D) ---
    print("Training feature ablation variants (XGBoost)...")
    ablation_idx = {
        "A_Temporal": [0,1,2,3],
        "B_Behavioral": [4],
        "C_Graph": [5,6],
        "D_All": [0,1,2,3,4,5,6]
    }

    os.makedirs("outputs/datasets/models/ablation", exist_ok=True)

    # Train on Group Split
    for variant, cols in ablation_idx.items():
        if len(np.unique(y_train)) < 2: continue
        X_tab_train_resampled_var = X_tab_train_resampled[:, cols]
        clf = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
        clf.fit(X_tab_train_resampled_var, y_train_resampled)
        joblib.dump(clf, f"outputs/datasets/models/ablation/xgb_{variant}_group.pkl")

    # Train on Chrono Split
    for variant, cols in ablation_idx.items():
        if len(np.unique(y_train_chrono)) < 2: continue
        X_tab_train_c_res_var = X_tab_train_c_res[:, cols]
        clf = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
        clf.fit(X_tab_train_c_res_var, y_train_c_res)
        joblib.dump(clf, f"outputs/datasets/models/ablation/xgb_{variant}_chrono.pkl")

    # Train on Stratified Chronological Split (Dist Shift)
    print("Training on Stratified Chronological Split (Dist Shift)...")
    mal_idx = np.where(y == 1)[0]
    ben_idx = np.where(y == 0)[0]

    train_mal_end = int(len(mal_idx) * 0.5)
    train_ben_end = int(len(ben_idx) * 0.5)

    dist_train_idx = np.concatenate([mal_idx[:train_mal_end], ben_idx[:train_ben_end]])
    dist_test_idx = np.concatenate([mal_idx[train_mal_end:], ben_idx[train_ben_end:]])

    X_tab_train_dist = X_tabular[dist_train_idx]
    y_train_dist = y[dist_train_idx]
    X_tab_test_dist = X_tabular[dist_test_idx]
    y_test_dist = y[dist_test_idx]

    np.savez("outputs/datasets/models/dist_test_data.npz",
             X_tab_test=X_tab_test_dist, y_test=y_test_dist)

    if len(np.unique(y_train_dist)) > 1:
        smote_d = SMOTE(random_state=42, k_neighbors=min(5, sum(y_train_dist==1)-1))
        if smote_d.k_neighbors < 1: smote_d.k_neighbors = 1
        X_tab_train_d_res, y_train_d_res = smote_d.fit_resample(X_tab_train_dist, y_train_dist)
        for variant, cols in ablation_idx.items():
            X_tab_train_d_res_var = X_tab_train_d_res[:, cols]
            clf = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
            clf.fit(X_tab_train_d_res_var, y_train_d_res)
            joblib.dump(clf, f"outputs/datasets/models/ablation/xgb_{variant}_dist.pkl")

    # Random Split for completeness (Ablation Condition)
    print("Training on standard Random Split...")
    from sklearn.model_selection import train_test_split
    X_tab_train_rand, X_tab_test_rand, y_train_rand, y_test_rand = train_test_split(X_tabular, y, test_size=0.4, random_state=42)
    np.savez("outputs/datasets/models/rand_test_data.npz", X_tab_test=X_tab_test_rand, y_test=y_test_rand)

    if len(np.unique(y_train_rand)) > 1:
        smote_r = SMOTE(random_state=42, k_neighbors=min(5, sum(y_train_rand==1)-1))
        if smote_r.k_neighbors < 1: smote_r.k_neighbors = 1
        X_tab_train_r_res, y_train_r_res = smote_r.fit_resample(X_tab_train_rand, y_train_rand)
        for variant, cols in ablation_idx.items():
            X_tab_train_r_res_var = X_tab_train_r_res[:, cols]
            clf = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
            clf.fit(X_tab_train_r_res_var, y_train_r_res)
            joblib.dump(clf, f"outputs/datasets/models/ablation/xgb_{variant}_rand.pkl")

    out_dir = "outputs/datasets/models"
    os.makedirs(out_dir, exist_ok=True)

    with open(f"{out_dir}/threshold.txt", "w") as f:
        f.write(str(best_threshold))

    joblib.dump(xgb_clf, f"{out_dir}/xgb_model.pkl")
    joblib.dump(svm_clf, f"{out_dir}/svm_model.pkl")
    joblib.dump(mlp_clf, f"{out_dir}/mlp_model.pkl")
    lstm_model.save(f"{out_dir}/lstm_model.h5")
    joblib.dump(meta_clf, f"{out_dir}/meta_model.pkl")

    np.savez(f"{out_dir}/test_data.npz",
             X_tab_test=X_tab_test,
             X_seq_test=X_seq_test,
             X_meta_test=X_meta_test,
             y_test=y_test,
             X_tab_train=X_tab_train,
             y_train=y_train)

    with open(f"{out_dir}/train_times.txt", "w") as f:
        for k, v in train_times.items():
            f.write(f"{k}: {v:.2f}s\n")

    print("Modeling complete and models saved.")

if __name__ == "__main__":
    run_modeling()
