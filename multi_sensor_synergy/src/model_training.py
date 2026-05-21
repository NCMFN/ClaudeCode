"""Train all 5 classifiers, cross-validation."""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import config
from feature_engineering import apply_smote

def get_models():
    """Return a dictionary of the 5 classifiers to train."""
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=None, random_state=config.RANDOM_STATE, n_jobs=-1),
        'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=config.RANDOM_STATE, n_jobs=-1),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=config.RANDOM_STATE, n_jobs=-1),
        'Decision Tree': DecisionTreeClassifier(random_state=config.RANDOM_STATE),
        'SVM': SVC(kernel='rbf', probability=True, random_state=config.RANDOM_STATE, max_iter=2000)
    }
    return models


from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

def train_and_save_models(X_train, y_train):
    print("Applying SMOTE on training data and running CV...")

    # Subsample if dataset is too large to train quickly
    if len(X_train) > 20000:
        print(f"Subsampling to 20000 for faster training...")
        idx = np.random.choice(len(X_train), 20000, replace=False)
        X_train_sub = X_train.iloc[idx]
        y_train_sub = y_train.iloc[idx]
    else:
        X_train_sub = X_train
        y_train_sub = y_train

    models = get_models()
    skf = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE)

    for name, model in models.items():
        print(f"Running CV for {name}...")

        # Create pipeline to prevent data leakage during CV
        pipeline = ImbPipeline([
            ('smote', SMOTE(random_state=config.RANDOM_STATE)),
            ('classifier', model)
        ])

        cv_scores = cross_val_score(pipeline, X_train_sub, y_train_sub, cv=skf, scoring='f1_weighted', n_jobs=-1)
        print(f"{name} CV F1 Weighted: {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")

        print(f"Training final {name} model...")
        # Train final model on full resampled training set
        X_resampled, y_resampled = apply_smote(X_train_sub, y_train_sub)
        model.fit(X_resampled, y_resampled)

        model_path = os.path.join(config.MODELS_DIR, f"{name.replace(' ', '_').lower()}.pkl")
        joblib.dump(model, model_path)
        print(f"Saved {name} to {model_path}")

    return models


if __name__ == "__main__":
    df = pd.read_csv(config.FEATURE_DATA_PATH)

    X = df.drop(columns=['Intervention_Required'])
    y = df['Intervention_Required']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y)

    train_and_save_models(X_train, y_train)
