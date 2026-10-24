import pytest
import pandas as pd
import sys
sys.path.append('src')
from splits import leakage_check

def test_leakage_check_passes():
    df = pd.DataFrame({'time': [1, 2, 3, 10, 11, 12]})
    train_idx = [0, 1, 2]
    test_idx = [3, 4, 5]
    # Should not raise
    leakage_check(train_idx, test_idx, df, "chronological_holdout")

def test_leakage_check_fails():
    df = pd.DataFrame({'time': [1, 2, 10, 3, 11, 12]})
    train_idx = [0, 1, 2] # max time is 10
    test_idx = [3, 4, 5]  # min time is 3
    with pytest.raises(AssertionError):
        leakage_check(train_idx, test_idx, df, "chronological_holdout")
