import pytest
import pandas as pd
import numpy as np
from src.feature_engineer import KinematicFeatureEngineer

def test_feature_engineering():
    df = pd.DataFrame({
        'MMSI': [1, 1, 1],
        'BaseDateTime': pd.to_datetime(['2024-01-01 10:00:00', '2024-01-01 11:00:00', '2024-01-01 12:00:00']),
        'LAT': [40.0, 40.1, 40.5],
        'LON': [-74.0, -74.1, -74.5],
        'SOG': [10.0, 15.0, 0.1],
        'COG': [90.0, 0.0, 180.0],
        'Heading': [90.0, 0.0, 180.0],
        'VesselType': ['cargo', 'cargo', 'cargo'],
        'Draft': [10.0, 10.0, 10.0],
        'dest_lat': [40.5, 40.5, 40.5],
        'dest_lon': [-74.5, -74.5, -74.5],
        'dist_to_dest_km': [30.0, 15.0, 0.5]
    })

    engineer = KinematicFeatureEngineer()
    df_feat = engineer.transform(df)

    assert len(df_feat) == 2 # The last row has ETA <= 0 (it is the arrival timestamp)

    # Check SOG conversion
    assert np.isclose(df_feat.iloc[0]['SOG_kmh'], 10.0 * 1.852)

    # Check circular encoding for COG=90 -> sin=1, cos=0
    assert np.isclose(df_feat.iloc[0]['COG_sin'], 1.0)
    assert np.isclose(df_feat.iloc[0]['COG_cos'], 0.0, atol=1e-7)

    # Check circular encoding for COG=0 -> sin=0, cos=1
    assert np.isclose(df_feat.iloc[1]['COG_sin'], 0.0, atol=1e-7)
    assert np.isclose(df_feat.iloc[1]['COG_cos'], 1.0)

    # Check MKZ
    assert df_feat.iloc[0]['is_micro_kinematic_zone'] == 1 # dist = 30 < 50

    # Check ETA
    assert (df_feat['ETA_hours'] > 0).all()
    assert (df_feat['ETA_hours'] <= 168).all()
