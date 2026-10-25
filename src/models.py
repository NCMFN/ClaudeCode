from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
import xgboost as xgb
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_models(seed: int = 42) -> Dict[str, Any]:
    """Return instantiated models."""
    logger.info("Initializing models...")

    # Strictly define models based on requirements
    models = {
        'LogisticRegression': LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=seed,
            n_jobs=-1
        ),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            scale_pos_weight=100, # Handled loosely, but we evaluate with PR-AUC so it's okay
            random_state=seed,
            n_jobs=-1
        ),
        'IsolationForest': IsolationForest(
            n_estimators=100,
            contamination=0.01, # Rough estimate for anomalies
            random_state=seed,
            n_jobs=-1
        )
    }
    return models
