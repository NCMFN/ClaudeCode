import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import logging

class LinearBaselineModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('lr', Ridge(alpha=1.0))
        ])

    def fit(self, X, y):
        self.logger.info("Training Linear Regression (Ridge) baseline...")
        self.pipeline.fit(X, y)
        self.logger.info("Training complete.")

    def predict(self, X):
        return self.pipeline.predict(X)

    def evaluate(self, X, y):
        preds = self.predict(X)
        rmse = np.sqrt(mean_squared_error(y, preds))
        mae = mean_absolute_error(y, preds)
        r2 = r2_score(y, preds)

        self.logger.info(f"LR Baseline Evaluation -> RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
        return {'rmse': rmse, 'mae': mae, 'r2': r2}, preds

    def save(self, model_path):
        joblib.dump(self.pipeline, model_path)
        self.logger.info(f"Saved LR model to {model_path}")
