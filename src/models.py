from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
import xgboost as xgb

def get_models():
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "IsolationForest": IsolationForest(random_state=42),
        "XGBoost": xgb.XGBClassifier(random_state=42, eval_metric='logloss')
    }
