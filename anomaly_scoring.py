import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, RepeatVector, TimeDistributed, Dense

def build_lstm_autoencoder(timesteps, n_features):
    model = Sequential([
        LSTM(32, activation='relu', input_shape=(timesteps, n_features), return_sequences=True),
        LSTM(16, activation='relu', return_sequences=False),
        RepeatVector(timesteps),
        LSTM(16, activation='relu', return_sequences=True),
        LSTM(32, activation='relu', return_sequences=True),
        TimeDistributed(Dense(n_features))
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def create_sequences(X, time_steps):
    Xs = []
    for i in range(len(X) - time_steps + 1):
        Xs.append(X[i:(i + time_steps)])
    return np.array(Xs)

def detect_micro_anomalies(df: pd.DataFrame, features: list) -> pd.DataFrame:
    df = df.copy()
    df['if_anomaly'] = 0
    df['lstm_anomaly'] = 0
    df['micro_anomaly'] = 0

    for machine_id, group in df.groupby('machine_id'):
        X = group[features].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        preds = iso_forest.fit_predict(X_scaled)
        if_anom = (preds == -1).astype(int)
        df.loc[group.index, 'if_anomaly'] = if_anom

        time_steps = 5
        if len(X_scaled) > time_steps:
            X_seq = create_sequences(X_scaled, time_steps)

            callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=1)
            lstm_ae = build_lstm_autoencoder(time_steps, X_scaled.shape[1])
            lstm_ae.fit(X_seq, X_seq, epochs=1, batch_size=256, callbacks=[callback], verbose=0)

            X_pred = lstm_ae.predict(X_seq, verbose=0)
            mae = np.mean(np.abs(X_pred - X_seq), axis=(1, 2))

            mae_padded = np.pad(mae, (time_steps - 1, 0), 'constant', constant_values=np.mean(mae))

            threshold = np.mean(mae_padded) + 2 * np.std(mae_padded)
            lstm_anomalies = (mae_padded > threshold).astype(int)
            df.loc[group.index, 'lstm_anomaly'] = lstm_anomalies

            df.loc[group.index, 'micro_anomaly'] = ((df.loc[group.index, 'if_anomaly'] == 1) | (df.loc[group.index, 'lstm_anomaly'] == 1)).astype(int)
        else:
            df.loc[group.index, 'micro_anomaly'] = if_anom

    return df

def compute_risk_score(df: pd.DataFrame, alpha=0.45, beta=0.30, gamma=0.25) -> pd.DataFrame:
    df = df.copy()

    for machine_id, group in df.groupby('machine_id'):
        idx = group.index

        vib_anom_rate = group['micro_anomaly'].rolling(60, min_periods=1).mean()
        press_var = group['press_var']
        eng_spike = group['eng_spike_count']

        scaler = MinMaxScaler(feature_range=(0, 100))

        def scale_component(series):
            s_filled = series.fillna(0)
            if s_filled.max() == s_filled.min():
                return pd.Series(0, index=s_filled.index)
            return pd.Series(scaler.fit_transform(s_filled.values.reshape(-1, 1)).flatten(), index=s_filled.index)

        c1 = scale_component(vib_anom_rate)
        c2 = scale_component(press_var)
        c3 = scale_component(eng_spike)

        risk = alpha * c1 + beta * c2 + gamma * c3

        df.loc[idx, 'risk_score'] = risk
        df.loc[idx, 'high_risk_flag'] = (risk > 75).astype(int)

    return df
