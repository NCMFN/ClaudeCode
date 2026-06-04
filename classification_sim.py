import pandas as pd
import numpy as np
import os
import joblib
import logging
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import classification_report, roc_auc_score, roc_curve, confusion_matrix, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def calculate_lead_time(df, y_pred, threshold=0.5):
    lead_times = []

    df_eval = df[['machine_id', 'timestamp', 'maintenance_required']].copy()
    df_eval['pred'] = (y_pred >= threshold).astype(int)

    for machine_id, group in df_eval.groupby('machine_id'):
        failures = group[group['maintenance_required'] == 1]

        for fail_idx in failures.index:
            fail_time = failures.loc[fail_idx, 'timestamp']

            window_start = fail_time - pd.Timedelta(minutes=2880) # 48 hours = 2880 mins
            prior_preds = group[(group['timestamp'] >= window_start) & (group['timestamp'] < fail_time)]

            if len(prior_preds) > 0:
                flagged = prior_preds[prior_preds['pred'] == 1]
                if len(flagged) > 0:
                    first_flag_time = flagged['timestamp'].min()
                    lead_time_min = (fail_time - first_flag_time).total_seconds() / 60.0
                    lead_times.append(lead_time_min)
                else:
                    lead_times.append(0)
            else:
                lead_times.append(0)

    if len(lead_times) > 0:
        return np.mean(lead_times)
    return 0

def create_lstm_sequences(X, y, groups, timestamps, time_steps=60):
    Xs, ys, gs, ts = [], [], [], []

    df_temp = pd.DataFrame(X)
    df_temp['group'] = groups
    df_temp['y'] = y
    df_temp['timestamp'] = timestamps

    for g in np.unique(groups):
        g_data = df_temp[df_temp['group'] == g].sort_values('timestamp')
        g_X = g_data.drop(['group', 'y', 'timestamp'], axis=1).values
        g_y = g_data['y'].values
        g_t = g_data['timestamp'].values

        for i in range(len(g_X) - time_steps):
            Xs.append(g_X[i:(i + time_steps)])
            ys.append(g_y[i + time_steps])
            gs.append(g)
            ts.append(g_t[i + time_steps])

    return np.array(Xs), np.array(ys), np.array(gs), np.array(ts)

def train_and_evaluate_models(df: pd.DataFrame, features: list, target: str):
    X = df[features].values
    y = df[target].values
    groups = df['machine_id'].values

    gkf = GroupKFold(n_splits=5)

    models = {
        'RandomForest': RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1, max_depth=10),
        'XGBoost': XGBClassifier(n_estimators=50, learning_rate=0.1, random_state=42, eval_metric='logloss', max_depth=6)
    }

    results = {}

    for model_name, model in models.items():
        logging.info(f"Training {model_name}...")

        oof_preds = np.zeros(len(df))
        oof_probs = np.zeros(len(df))

        for train_idx, val_idx in gkf.split(X, y, groups):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            model.fit(X_train, y_train)

            oof_preds[val_idx] = model.predict(X_val)
            oof_probs[val_idx] = model.predict_proba(X_val)[:, 1]

        prec = precision_score(y, oof_preds, zero_division=0)
        rec = recall_score(y, oof_preds, zero_division=0)
        f1 = f1_score(y, oof_preds, zero_division=0)
        auc = roc_auc_score(y, oof_probs)

        lead_time = calculate_lead_time(df, oof_preds)

        results[model_name] = {
            'Precision': prec,
            'Recall': rec,
            'F1-Score': f1,
            'ROC-AUC': auc,
            'Lead Time (min)': lead_time,
            'Model': model,
            'Probs': oof_probs
        }

        logging.info(f"{model_name} - Prec: {prec:.4f}, Rec: {rec:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}, Lead Time: {lead_time:.2f} min")

        os.makedirs('models', exist_ok=True)
        joblib.dump(model, f'models/{model_name}.joblib')

    logging.info("Training LSTM Sequence Model...")

    train_idx, val_idx = next(gkf.split(X, y, groups))

    df_train = df.iloc[train_idx].copy()
    df_val = df.iloc[val_idx].copy()

    X_train_seq, y_train_seq, _, _ = create_lstm_sequences(df_train[features].values, df_train[target].values, df_train['machine_id'].values, df_train['timestamp'].values, time_steps=60)
    X_val_seq, y_val_seq, val_gs_seq, val_ts_seq = create_lstm_sequences(df_val[features].values, df_val[target].values, df_val['machine_id'].values, df_val['timestamp'].values, time_steps=60)

    lstm_model = Sequential([
        LSTM(32, input_shape=(60, len(features))),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])

    lstm_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)

    lstm_model.fit(X_train_seq, y_train_seq, validation_data=(X_val_seq, y_val_seq), epochs=5, batch_size=256, callbacks=[early_stop], verbose=1)

    lstm_probs = lstm_model.predict(X_val_seq).flatten()
    lstm_preds = (lstm_probs >= 0.5).astype(int)

    prec = precision_score(y_val_seq, lstm_preds, zero_division=0)
    rec = recall_score(y_val_seq, lstm_preds, zero_division=0)
    f1 = f1_score(y_val_seq, lstm_preds, zero_division=0)
    auc = roc_auc_score(y_val_seq, lstm_probs)

    df_val_eval = pd.DataFrame({
        'machine_id': val_gs_seq,
        'timestamp': val_ts_seq,
        'maintenance_required': y_val_seq
    })

    lead_time = calculate_lead_time(df_val_eval, lstm_preds)

    results['LSTM'] = {
        'Precision': prec,
        'Recall': rec,
        'F1-Score': f1,
        'ROC-AUC': auc,
        'Lead Time (min)': lead_time,
        'Model': lstm_model,
    }

    logging.info(f"LSTM - Prec: {prec:.4f}, Rec: {rec:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}, Lead Time: {lead_time:.2f} min")
    lstm_model.save('models/LSTM.keras')

    return results

def simulate_cloud_edge(df: pd.DataFrame):
    total_records = len(df)
    transmitted_records = len(df[df['risk_score'] > 75])
    reduction_pct = (1.0 - (transmitted_records / total_records)) * 100

    logging.info(f"Total Records: {total_records}")
    logging.info(f"Transmitted Records (Risk > 75): {transmitted_records}")
    logging.info(f"Bandwidth Reduction: {reduction_pct:.2f}%")

    return total_records, transmitted_records, reduction_pct
