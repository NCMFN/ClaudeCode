import pandas as pd
import joblib
import sys
import os

# Fix joblib unpickling issue by explicitly exposing the custom class in the main namespace
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train import XGBoostWithEarlyStopping
import __main__
setattr(__main__, 'XGBoostWithEarlyStopping', XGBoostWithEarlyStopping)

def predict_los(age: int, comorbidities_count: int, treatment_type: str,
                medications_count: int, primary_diagnosis: str, admission_date: str) -> float:
    """
    Predicts hospital Length of Stay (LOS) in days for a single patient.

    Args:
        age (int): Patient age
        comorbidities_count (int): Number of comorbidities (0-10)
        treatment_type (str): 'Medical' or 'Surgical'
        medications_count (int): Intensity of clinical regimen
        primary_diagnosis (str): E.g., 'Sepsis', 'Cardiac', etc.
        admission_date (str): 'YYYY-MM-DD' or similar format parseable by pandas

    Returns:
        float: Predicted Length of Stay in days
    """
    try:
        pipeline = joblib.load("outputs/xgb_los_model.pkl")
    except FileNotFoundError:
        try:
            pipeline = joblib.load("hospital-los-prediction/outputs/xgb_los_model.pkl")
        except FileNotFoundError:
            raise Exception("Model file not found. Ensure train.py has been run successfully.")

    date_parsed = pd.to_datetime(admission_date)
    admission_month = date_parsed.month
    admission_dayofweek = date_parsed.dayofweek

    if admission_month in [12, 1, 2]:
        admission_season = 'Winter'
    elif admission_month in [3, 4, 5]:
        admission_season = 'Spring'
    elif admission_month in [6, 7, 8]:
        admission_season = 'Summer'
    else:
        admission_season = 'Fall'

    input_data = pd.DataFrame([{
        'Age': age,
        'comorbidities_count': comorbidities_count,
        'treatment_type': treatment_type,
        'medications_count': medications_count,
        'primary_diagnosis': primary_diagnosis,
        'admission_month': admission_month,
        'admission_season': admission_season,
        'admission_dayofweek': admission_dayofweek
    }])

    prediction = pipeline.predict(input_data)[0]
    return float(prediction)

if __name__ == "__main__":
    pred = predict_los(
        age=65,
        comorbidities_count=3,
        treatment_type="Medical",
        medications_count=12,
        primary_diagnosis="Sepsis",
        admission_date="2023-11-15"
    )
    print(f"Predicted LOS: {pred:.2f} days")
