import pytest
import os
import sys
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.data_loader import NavalPropulsionLoader

def test_data_loader():
    filepath = os.path.join(config.RAW_DATA_DIR, "UCI CBM Dataset", "data.txt")
    loader = NavalPropulsionLoader()

    df = loader.load(filepath)
    assert df.shape[1] == 18, f"Expected 18 columns, got {df.shape[1]}"

    assert not df.isna().any().any(), "Found NaN values in dataset"
    assert not np.isinf(df.values).any(), "Found inf values in dataset"

    assert df['kMc'].between(0.9, 1.0).all(), "kMc range out of bounds"
    assert df['kMt'].between(0.9, 1.0).all(), "kMt range out of bounds"
