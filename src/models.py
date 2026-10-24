import os
import csv
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import precision_recall_curve
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding

from config import SEED

def get_class_weights(y):
    neg = np.sum(y == 0)
    pos = np.sum(y == 1)
    if pos == 0:
        return {0: 1.0, 1: 1.0}
    total = len(y)
    return {0: (1 / neg) * (total / 2.0), 1: (1 / pos) * (total / 2.0)}

class LSTMModel:
    def __init__(self, vocab_size=50, seq_len=10):
        tf.random.set_seed(SEED)
        self.model = Sequential([
            Embedding(input_dim=vocab_size, output_dim=8, input_length=seq_len),
            LSTM(16),
            Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy')

    def fit(self, X, y, class_weight=None, epochs=5, batch_size=32):
        self.model.fit(X, y, class_weight=class_weight, epochs=epochs, batch_size=batch_size, verbose=0)

    def predict_proba(self, X):
        preds = self.model.predict(X, verbose=0)
        return np.hstack([1 - preds, preds])

def train_base_models(X_train, y_train, X_train_seq):
    cw = get_class_weights(y_train)

    # 1. Logistic Regression
    lr = LogisticRegression(random_state=SEED, class_weight='balanced', max_iter=1000)
    lr.fit(X_train, y_train)

    # 2. XGBoost
    xgb_model = xgb.XGBClassifier(random_state=SEED, scale_pos_weight=cw[1]/cw[0], eval_metric='logloss')
    xgb_model.fit(X_train, y_train)

    # 3. RBF-SVM with probability calibration
    svm = SVC(kernel='rbf', probability=True, random_state=SEED, class_weight='balanced')
    svm.fit(X_train, y_train)

    # 4. MLP
    mlp = MLPClassifier(random_state=SEED, max_iter=500)
    mlp.fit(X_train, y_train)

    # 5. LSTM
    lstm = LSTMModel()
    lstm.fit(X_train_seq, y_train, class_weight=cw)

    return {
        'lr': lr,
        'xgb': xgb_model,
        'svm': svm,
        'mlp': mlp,
        'lstm': lstm
    }

def train_negative_controls(X_train_time, y_train, X_train_shuffle, y_train_shuffle):
    """
    Control 1: Time-only features
    Control 2: Label-shuffle (seeded)
    """
    time_model = xgb.XGBClassifier(random_state=SEED, eval_metric='logloss')
    time_model.fit(X_train_time, y_train)

    shuffle_model = xgb.XGBClassifier(random_state=SEED, eval_metric='logloss')
    shuffle_model.fit(X_train_shuffle, y_train_shuffle)

    return time_model, shuffle_model

def get_out_of_fold_predictions(df, feature_cols, folds):
    from features import build_features, extract_X_y
    # To properly stack, we need out of fold predictions for the meta classifier.
    # In time series, OOF must be time-ordered.
    oof_preds = []

    # We will simply use the chronological holdout folds to simulate a valid OOF?
    # No, to train the meta classifier, we can train base models on train folds and predict on val folds.
    # We'll just assume we're provided a list of (train_idx, val_idx) for OOF generation.

    for train_idx, val_idx in folds:
        df_feat, _ = build_features(df, train_idx=train_idx, use_temporal=True)
        X_train, X_train_seq, y_train = extract_X_y(df_feat.iloc[train_idx], feature_cols)
        X_val, X_val_seq, y_val = extract_X_y(df_feat.iloc[val_idx], feature_cols)

        models = train_base_models(X_train, y_train, X_train_seq)

        fold_preds = pd.DataFrame({'idx': val_idx, 'label': y_val})
        for name, m in models.items():
            if name == 'lstm':
                fold_preds[name] = m.predict_proba(X_val_seq)[:, 1]
            else:
                fold_preds[name] = m.predict_proba(X_val)[:, 1]
        oof_preds.append(fold_preds)

    return pd.concat(oof_preds).sort_values('idx')

def train_meta_classifier(oof_df):
    X_meta = oof_df[['lr', 'xgb', 'svm', 'mlp', 'lstm']].values
    y_meta = oof_df['label'].values

    meta = LogisticRegression(random_state=SEED, class_weight='balanced')
    meta.fit(X_meta, y_meta)

    # Choose threshold on OOF set
    probas = meta.predict_proba(X_meta)[:, 1]
    precisions, recalls, thresholds = precision_recall_curve(y_meta, probas)

    # F1 score threshold
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-10)
    best_idx = np.argmax(f1_scores)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else 0.5

    return meta, best_threshold

def save_models(models, meta_model, threshold):
    os.makedirs("outputs/datasets/models", exist_ok=True)
    for name, m in models.items():
        if name == 'lstm':
            m.model.save("outputs/datasets/models/lstm.keras")
        else:
            joblib.dump(m, f"outputs/datasets/models/{name}.pkl")

    joblib.dump(meta_model, "outputs/datasets/models/meta.pkl")

    os.makedirs("outputs/tables", exist_ok=True)
    with open("outputs/tables/model_cards.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["model", "hyperparameters", "threshold"])
        for name, m in models.items():
            if name == 'lstm':
                writer.writerow([name, "vocab=50, layers=LSTM(16)", "-"])
            else:
                writer.writerow([name, str(m.get_params()), "-"])
        writer.writerow(["meta_classifier", str(meta_model.get_params()), threshold])
