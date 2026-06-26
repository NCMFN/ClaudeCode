import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from sklearn.model_selection import train_test_split

def main():
    ts_df = pd.read_parquet("data/processed/heliospredict_processed.parquet")
    labels_df = pd.read_csv("data/processed/features_daily.csv")
    ts_df = ts_df.merge(labels_df[['session_id', 'meets_25pct_threshold', 'predicted_exposure_hours']], on='session_id', how='left').fillna(0)

    xs, ys_c, ys_r = [], [], []
    features = ['lux_scaled', 'uv_index_scaled', 'hour_z', 'day_of_year_z', 'is_outdoor']
    for _, group in ts_df.groupby('session_id'):
        data = group.sort_values('time')[features].values
        for i in range(len(data) - 11):
            xs.append(data[i:i+12]); ys_c.append(group['meets_25pct_threshold'].iloc[0]); ys_r.append(group['predicted_exposure_hours'].iloc[0])

    X, y_c, y_r = np.array(xs, dtype=np.float32), np.array(ys_c, dtype=np.float32), np.array(ys_r, dtype=np.float32)
    if len(X)==0: return

    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_c, test_size=0.15, random_state=42)
    model_c = Sequential([Input(shape=(12, 5)), LSTM(32), Dense(1, activation='sigmoid')])
    model_c.compile(optimizer='adam', loss='binary_crossentropy')
    model_c.fit(X_train_c, y_train_c, epochs=5, verbose=0)
    model_c.save("outputs/models/lstm_classifier.h5")

    pd.DataFrame([{"Model": "LSTM"}]).to_csv("outputs/tables/lstm_results.csv", index=False)
if __name__ == "__main__": main()
