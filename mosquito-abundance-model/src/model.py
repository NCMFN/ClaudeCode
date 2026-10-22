import pandas as pd
import numpy as np
import yaml
import logging
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import optuna
from sklearn.model_selection import KFold
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path="config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

class MosquitoLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(MosquitoLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out

def spatial_block_cv(df, n_blocks=5, random_state=42):
    np.random.seed(random_state)

    # We will use simple pandas qcut, but we must handle the ArrowStringArray issue
    # by converting to a regular numpy array or list before shuffling.

    # If the variance in coords is too low, qcut will fail, so we add tiny noise
    lat = df['latitude'].values + np.random.normal(0, 1e-6, len(df))
    lon = df['longitude'].values + np.random.normal(0, 1e-6, len(df))

    lat_bins = pd.qcut(lat, q=max(2, int(np.sqrt(n_blocks))), labels=False, duplicates='drop')
    lon_bins = pd.qcut(lon, q=max(2, int(np.sqrt(n_blocks))), labels=False, duplicates='drop')

    blocks = [f"{la}_{lo}" for la, lo in zip(lat_bins, lon_bins)]
    df_blocks = pd.Series(blocks)

    unique_blocks = list(df_blocks.unique())
    np.random.shuffle(unique_blocks)

    folds = np.array_split(unique_blocks, n_blocks)

    for val_blocks in folds:
        val_idx = df.index[df_blocks.isin(val_blocks)].tolist()
        train_idx = df.index[~df_blocks.isin(val_blocks)].tolist()

        # Ensure we don't return empty folds
        if len(val_idx) > 0 and len(train_idx) > 0:
            yield train_idx, val_idx

def prepare_data_for_models(df, target_col='y_log1p'):
    features = [
        'latitude', 'longitude', 'elevation', 'degree_days_accum', 'humidity_index',
        'tp_lag0', 'tp_lag7', 'tp_lag14', 't2m_mean', 't2m_max', 't2m_min',
        'diurnal_temp_range', 'lst_proxy', 'sin_doy', 'cos_doy'
    ]

    X = df[features].values
    y = df[target_col].values

    return X, y, features

def train_rf(X, y, df_source):
    logger.info("Training Random Forest baseline...")
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)

    model.fit(X, y)

    os.makedirs('outputs/models', exist_ok=True)
    joblib.dump(model, 'outputs/models/rf_model.pkl')
    return model

def optimize_xgb(X, y, df_source):
    logger.info("Optimizing XGBoost with Spatial CV using Optuna...")

    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 200),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'random_state': 42
        }

        cv_scores = []
        for train_idx, val_idx in spatial_block_cv(df_source, n_blocks=3):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            if len(X_train) == 0 or len(X_val) == 0:
                continue

            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train)
            preds = model.predict(X_val)
            rmse = np.sqrt(mean_squared_error(y_val, preds))
            cv_scores.append(rmse)

        return np.mean(cv_scores) if cv_scores else float('inf')

    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=3)

    logger.info(f"Best XGB Params: {study.best_params}")

    best_params = study.best_params
    best_params['random_state'] = 42
    final_model = xgb.XGBRegressor(**best_params)
    final_model.fit(X, y)

    joblib.dump(final_model, 'outputs/models/xgb_model.pkl')
    return final_model

def train_lstm(df_source):
    logger.info("Training LSTM...")
    X_tab, y, features = prepare_data_for_models(df_source)

    seq_length = 4
    n_samples, n_features = X_tab.shape

    X_seq = np.zeros((n_samples, seq_length, n_features))
    for i in range(seq_length):
        X_seq[:, i, :] = X_tab + np.random.normal(0, 0.01, size=X_tab.shape)

    X_tensor = torch.FloatTensor(X_seq)
    y_tensor = torch.FloatTensor(y).view(-1, 1)

    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=128, shuffle=True)

    model = MosquitoLSTM(input_size=n_features)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    epochs = 5
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for batch_X, batch_y in loader:
            optimizer.zero_grad()
            out = model(batch_X)
            loss = criterion(out, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        logger.info(f"LSTM Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(loader):.4f}")

    torch.save(model.state_dict(), 'outputs/models/lstm_model.pth')
    return model

def run_models(config):
    in_path = config['data']['features_parquet']
    df = pd.read_parquet(in_path)

    df = df.reset_index(drop=True)

    X, y, features = prepare_data_for_models(df)

    train_rf(X, y, df)
    optimize_xgb(X, y, df)
    train_lstm(df)

if __name__ == "__main__":
    config = load_config()
    run_models(config)
