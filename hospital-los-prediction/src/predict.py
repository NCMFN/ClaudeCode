import pandas as pd
import joblib
from features import engineer_features
from etl import extract_date_features

# Need to import XGBWrapper so joblib can unpickle it
from train import XGBWrapper

def predict_los(age: int, comorbidities_count: int, treatment_type: str,
                medications_count: int, primary_diagnosis: str, admission_date: str) -> float:
    """
    Returns predicted LOS in days for a single patient.
    """
    # Create DataFrame from input
    data = {
        'Age': [age],
        'comorbidities_count': [comorbidities_count],
        'treatment_type': [treatment_type],
        'medications_count': [medications_count],
        'primary_diagnosis': [primary_diagnosis],
        'Admission date': [admission_date]
    }
    df = pd.DataFrame(data)

    # Preprocess date
    df = extract_date_features(df, 'Admission date')

    # Feature engineering
    df = engineer_features(df)

    # Drop Admission date as in training
    X = df.drop(columns=['Admission date'])

    # Load model pipeline
    model_pipeline = joblib.load('outputs/xgb_los_model.pkl')

    # Predict
    pred = model_pipeline.predict(X)[0]
    return float(pred)

if __name__ == "__main__":
    # Test Prediction
    pred = predict_los(65, 3, "Medical", 10, "Cardiac", "2023-10-15")
    print(f"Predicted LOS: {pred:.2f} days")
