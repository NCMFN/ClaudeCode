import pandas as pd
import numpy as np
from src.phase2_features import temporal_encoding

def test_temporal_encoding():
    df = pd.DataFrame({
        'timestamp': [1420070400, 1420113600] # 2015-01-01 00:00:00 and 12:00:00
    })

    encoded = temporal_encoding(df)

    assert 'hour_sin' in encoded.columns
    assert 'hour_cos' in encoded.columns
    assert 'dow_sin' in encoded.columns
    assert 'dow_cos' in encoded.columns

    # 00:00 hour should have sin=0, cos=1
    assert np.isclose(encoded.loc[0, 'hour_sin'], 0.0, atol=1e-5)
    assert np.isclose(encoded.loc[0, 'hour_cos'], 1.0, atol=1e-5)

    # 12:00 hour should have sin=0, cos=-1
    assert np.isclose(encoded.loc[1, 'hour_sin'], 0.0, atol=1e-5)
    assert np.isclose(encoded.loc[1, 'hour_cos'], -1.0, atol=1e-5)
