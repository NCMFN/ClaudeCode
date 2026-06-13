import numpy as np

def generate_synthetic_data(modality: str, num_samples: int, noise_level: float = 0.1):
    """
    Generates synthetic data for a given modality.
    Returns (X, y) where X is the feature matrix and y is the label vector
    (1 for legitimate human action, 0 for spoofed/replayed).
    """
    if modality == "knock":
        # Features: mean interval, interval std, force variance
        # Humans have higher natural jitter (std) than replays
        X_human = np.random.normal(loc=[0.5, 0.05, 0.1], scale=[0.1, 0.02, 0.02], size=(num_samples // 2, 3))
        X_spoof = np.random.normal(loc=[0.5, 0.005, 0.01], scale=[0.1, 0.002, 0.002], size=(num_samples // 2, 3))
        y = np.array([1] * (num_samples // 2) + [0] * (num_samples // 2))
        X = np.vstack((X_human, X_spoof))

    elif modality == "touch":
        # Features: capacitance peak, decay rate, contact area
        # Real skin has specific capacitance profile
        X_human = np.random.normal(loc=[45.0, 0.8, 12.0], scale=[5.0, 0.1, 2.0], size=(num_samples // 2, 3))
        X_spoof = np.random.normal(loc=[20.0, 0.2, 5.0], scale=[2.0, 0.05, 1.0], size=(num_samples // 2, 3))
        y = np.array([1] * (num_samples // 2) + [0] * (num_samples // 2))
        X = np.vstack((X_human, X_spoof))

    elif modality == "gesture":
        # Features: 3D depth variance, trajectory smoothness, speed
        # Live gestures have depth, 2D replays are flat
        X_human = np.random.normal(loc=[15.0, 0.7, 1.2], scale=[3.0, 0.1, 0.2], size=(num_samples // 2, 3))
        X_spoof = np.random.normal(loc=[0.5, 0.9, 1.2], scale=[0.2, 0.05, 0.2], size=(num_samples // 2, 3))
        y = np.array([1] * (num_samples // 2) + [0] * (num_samples // 2))
        X = np.vstack((X_human, X_spoof))

    else:
        raise ValueError(f"Unknown modality: {modality}")

    # Inject noise into features based on noise_level
    noise = np.random.normal(0, noise_level, X.shape)
    X = X + (X * noise) # Relative noise scaling

    return X, y

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

def train_and_evaluate_classifiers(X, y):
    """
    Trains Logistic Regression and Random Forest classifiers.
    Returns evaluation metrics.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Logistic Regression
    lr = LogisticRegression(random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    y_prob_lr = lr.predict_proba(X_test)[:, 1]

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_prob_rf = rf.predict_proba(X_test)[:, 1]

    metrics = {
        "LR": {
            "accuracy": accuracy_score(y_test, y_pred_lr),
            "precision": precision_score(y_test, y_pred_lr, zero_division=0),
            "recall": recall_score(y_test, y_pred_lr, zero_division=0),
            "f1": f1_score(y_test, y_pred_lr, zero_division=0),
            "auc": roc_auc_score(y_test, y_prob_lr),
            "cm": confusion_matrix(y_test, y_pred_lr),
            "y_test": y_test,
            "y_prob": y_prob_lr
        },
        "RF": {
            "accuracy": accuracy_score(y_test, y_pred_rf),
            "precision": precision_score(y_test, y_pred_rf, zero_division=0),
            "recall": recall_score(y_test, y_pred_rf, zero_division=0),
            "f1": f1_score(y_test, y_pred_rf, zero_division=0),
            "auc": roc_auc_score(y_test, y_prob_rf),
            "cm": confusion_matrix(y_test, y_pred_rf),
            "y_test": y_test,
            "y_prob": y_prob_rf
        }
    }

    return metrics
