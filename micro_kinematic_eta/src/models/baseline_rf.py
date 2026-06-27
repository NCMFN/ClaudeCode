import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import logging
from config import RANDOM_SEED

class RFBaselineModel:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=RANDOM_SEED
        )

    def fit(self, X, y):
        self.logger.info("Training Random Forest baseline...")
        self.model.fit(X, y)
        self.logger.info("Training complete.")

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self, X, y):
        preds = self.predict(X)
        rmse = np.sqrt(mean_squared_error(y, preds))
        mae = mean_absolute_error(y, preds)
        r2 = r2_score(y, preds)

        self.logger.info(f"RF Baseline Evaluation -> RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")
        return {'rmse': rmse, 'mae': mae, 'r2': r2}, preds

    def save(self, model_path):
        joblib.dump(self.model, model_path)
        self.logger.info(f"Saved RF model to {model_path}")

    def save_feature_importance(self, feature_names, out_path):
        importance = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        importance.to_csv(out_path, index=False)
        self.logger.info(f"Saved RF feature importance to {out_path}")
