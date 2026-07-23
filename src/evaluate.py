import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

def evaluate_model(model, X_test, y_test, label_encoder):
    """
    Evaluates a trained model and returns metrics.
    """
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average='macro')
    cm = confusion_matrix(y_test, y_pred)

    report = classification_report(y_test, y_pred, target_names=label_encoder.classes_)

    return {
        'accuracy': acc,
        'f1_macro': f1_macro,
        'confusion_matrix': cm,
        'report': report
    }

def get_logistic_regression_odds_ratios(lr_pipeline, label_encoder):
    """
    Extracts coefficients from a Logistic Regression pipeline and converts them to odds ratios.
    """
    classifier = lr_pipeline.named_steps['classifier']
    preprocessor = lr_pipeline.named_steps['preprocessor']

    feature_names = preprocessor.get_feature_names_out()
    classes = label_encoder.classes_

    coefs = classifier.coef_
    odds_ratios = np.exp(coefs)

    or_df = pd.DataFrame(odds_ratios, columns=feature_names, index=classes)
    return or_df
