import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import time

def get_preprocessor(X):
    """
    Dynamically creates a preprocessing pipeline for numeric and categorical features.
    """
    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=[np.number]).columns.tolist()

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    return preprocessor

def get_models():
    """
    Returns a dictionary of un-fitted ML models wrapped in pipelines.
    """
    return {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100, n_jobs=-1),
        'XGBoost': XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss', n_jobs=-1)
    }

def train_and_predict(X_train, y_train, X_test, model_name, model, preprocessor):
    """
    Trains the model and returns predictions and timings.
    """
    pipe = Pipeline(steps=[('preprocessor', preprocessor),
                           ('classifier', model)])

    # Training
    t0 = time.time()
    pipe.fit(X_train, y_train)
    train_time = time.time() - t0

    # Inference
    t0 = time.time()
    y_pred = pipe.predict(X_test)
    y_proba = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, 'predict_proba') else y_pred
    inference_time = time.time() - t0

    # Calculate inference time per 1000 records
    inf_time_per_1000 = (inference_time / len(X_test)) * 1000 if len(X_test) > 0 else 0

    return y_pred, y_proba, train_time, inf_time_per_1000
