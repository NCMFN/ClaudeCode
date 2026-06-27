import pytest
import pandas as pd
import numpy as np
import datetime
from src.data_loader import AISDataLoader

@pytest.fixture
def sample_data():
    df = pd.DataFrame({
        'MMSI': [1, 2, 3, 4],
        'BaseDateTime': ['2024-01-01 10:00:00', '2024-01-01 11:00:00', '2024-01-01 12:00:00', '2030-01-01 10:00:00'],
        'LAT': [40.0, 91.0, 40.0, 40.0],
        'LON': [-74.0, -74.0, -74.0, -74.0],
        'SOG': [10.0, 10.0, 999.0, 10.0],
        'COG': [90.0, 90.0, 90.0, 90.0]
    })
    return df

def test_data_loader_validation(sample_data, tmp_path):
    # Write to temp csv
    csv_file = tmp_path / "test.csv"
    sample_data.to_csv(csv_file, index=False)

    loader = AISDataLoader()
    df = loader.load(str(csv_file))

    assert pd.api.types.is_datetime64_any_dtype(df['BaseDateTime'])

    df_clean, report = loader.validate(df)

    assert report['removed_lat'] == 1 # LAT 91.0
    assert report['removed_sog'] == 1 # SOG 999.0
    assert report['removed_future_time'] == 1 # 2030
    assert len(df_clean) == 1
    assert df_clean.iloc[0]['MMSI'] == 1
