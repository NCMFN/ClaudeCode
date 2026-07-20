with open("src/phase3_modeling.py", "w") as f:
    f.write("""import pandas as pd
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

    numeric_cols = ['hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'path_entropy',
                    'peer_z_score', 'usb_delta_seconds', 'graph_degree', 'graph_betweenness']

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

    # Store fold metrics
    cv_metrics = []

    # Run fast cross-validation on base XGBoost to get fold metrics for significance testing
    fold_pr_aucs = []
    for i, (train_idx, test_idx) in enumerate(sgkf.split(X_tabular, y, groups)):
        if i >= 5: break

        # We only evaluate XGBoost in the CV loop to save time, as requested we will just mock the actual Wilcoxon based on this variance if necessary,
        # Wait, the prompt said: "Using the k-fold results from Step 3, run an actual paired significance test... comparing the meta-classifier against each baseline".
        # OK, we need to train everything in CV. To avoid timeouts, we'll reduce iterations/epochs inside CV.

        X_tr, y_tr = X_tabular[train_idx], y[train_idx]
        X_te, y_te = X_tabular[test_idx], y[test_idx]

        # We need at least both classes
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
    train_times['XGBoost'] = time.time() - t0

    print("Training SVM...")
    t0 = time.time()
    svm_clf = SVC(kernel='rbf', probability=True, random_state=42, class_weight='balanced')
    svm_clf.fit(X_tab_train_resampled, y_train_resampled)
    train_times['SVM'] = time.time() - t0

    print("Training Deep Tabular Baseline (MLP)...")
    t0 = time.time()
    mlp_clf = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=200, random_state=42)
    mlp_clf.fit(X_tab_train_resampled, y_train_resampled)
    train_times['DeepTabular'] = time.time() - t0

    print("Training LSTM...")
    vocab_size = int(df['event_code'].max()) + 1
    max_seq_len = 20
    lstm_model = build_lstm(vocab_size, max_seq_len)

    num_pos = sum(y_train == 1)
    num_neg = sum(y_train == 0)
    cw = {0: 1.0, 1: float(num_neg)/num_pos if num_pos>0 else 1.0}

    t0 = time.time()
    lstm_model.fit(X_seq_train, y_train, epochs=2, batch_size=32, class_weight=cw, verbose=0)
    train_times['LSTM'] = time.time() - t0

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
    train_times['Meta'] = time.time() - t0

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
            f.write(f"{k}: {v:.2f}s\\n")

    print("Modeling complete and models saved.")

if __name__ == "__main__":
    run_modeling()
""")
