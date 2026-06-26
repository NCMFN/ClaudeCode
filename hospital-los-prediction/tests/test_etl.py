import pandas as pd
import numpy as np
from src.etl import synthesize_missing_features, handle_missing_values

def test_synthesize_missing_features():
    df = pd.DataFrame({'eid': [1, 2, 3]})
    df = synthesize_missing_features(df)
    assert 'Age' in df.columns
    assert 'treatment_type' in df.columns
    assert 'primary_diagnosis' in df.columns
    assert len(df) == 3

def test_handle_missing_values():
    df = pd.DataFrame({'a': [1, np.nan, 3], 'b': ['x', None, 'x']})
    df = handle_missing_values(df)
    assert df['a'].isnull().sum() == 0
    assert df['b'].isnull().sum() == 0
    assert df['a'].iloc[1] == 2.0
    assert df['b'].iloc[1] == 'x'
