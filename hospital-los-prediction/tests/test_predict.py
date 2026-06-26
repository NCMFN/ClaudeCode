import sys
import os

# Important: Add src to path so pytest/joblib can find 'train.py' and unpickle the custom class
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Also explicitly import the class into the module namespace so joblib can find it
import train
setattr(sys.modules[__name__], 'XGBoostWithEarlyStopping', train.XGBoostWithEarlyStopping)

from predict import predict_los

def test_predict_los_runs_successfully():
    # Make sure we can call it without errors and we get a reasonable output type (float)
    pred = predict_los(
        age=65,
        comorbidities_count=3,
        treatment_type="Medical",
        medications_count=12,
        primary_diagnosis="Sepsis",
        admission_date="2023-11-15"
    )
    assert isinstance(pred, float)
    assert pred > 0, "LOS should be purely positive."
