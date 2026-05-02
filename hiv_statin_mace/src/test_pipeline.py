import pytest
import numpy as np
from scores import calculate_framingham_risk, calculate_ascvd_risk

def test_framingham_risk():
    row = {
        'age': 50,
        'sex_at_birth': 1,
        'total_cholesterol': 200,
        'hdl_cholesterol': 50,
        'systolic_bp': 120,
        'bp_treatment': 0,
        'smoking_status': 'never',
        'diabetes_status': 0
    }
    risk = calculate_framingham_risk(row)
    assert 0 <= risk <= 1

def test_ascvd_risk():
    row = {
        'age': 50,
        'sex_at_birth': 1,
        'race': 'White',
        'total_cholesterol': 200,
        'hdl_cholesterol': 50,
        'systolic_bp': 120,
        'bp_treatment': 0,
        'smoking_status': 'never',
        'diabetes_status': 0
    }
    risk = calculate_ascvd_risk(row)
    assert 0 <= risk <= 1
