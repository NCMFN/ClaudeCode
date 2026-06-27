import pytest
import pandas as pd
import numpy as np
import os
from src.destination_clusterer import PortDestinationClusterer

def test_clusterer_fit_assign():
    df = pd.DataFrame({
        'LAT': [40.0, 40.01, 40.02, 34.0, 34.01, 34.02],
        'LON': [-74.0, -74.01, -74.02, -118.0, -118.01, -118.02],
        'SOG': [0.1, 0.2, 0.1, 0.2, 0.1, 0.3]
    })

    # ensure output dir exists
    os.makedirs('outputs/results', exist_ok=True)

    clusterer = PortDestinationClusterer(eps=0.5, min_samples=2)
    clusterer.fit(df)

    assert len(clusterer.port_centroids) > 0
    assert os.path.exists('outputs/results/port_clusters.csv')

    df_assigned = clusterer.assign_destination(df.copy())
    assert 'dist_to_dest_km' in df_assigned.columns
    assert (df_assigned['dist_to_dest_km'] >= 0).all()
