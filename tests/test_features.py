import pytest
import pandas as pd
import sys
sys.path.append('src')
from features import build_features

def test_features_no_future_leak():
    df = pd.DataFrame({
        'time': [10, 20, 30],
        'user': ['U1', 'U1', 'U1'],
        'src_comp': ['C1', 'C2', 'C1'],
        'auth_type': ['A', 'A', 'B'],
        'logon_type': ['L1', 'L1', 'L1'],
        'orientation': ['O1', 'O1', 'O1'],
        'success': ['Success', 'Fail', 'Success'],
        'second_of_day': [10, 20, 30],
        'label': [0, 0, 1]
    })

    df1, cols = build_features(df, train_idx=[0,1,2])

    # modify future event
    df2 = df.copy()
    df2.loc[2, 'success'] = 'Fail'
    df2, cols2 = build_features(df2, train_idx=[0,1,2])

    # Past features (at index 1) should be unchanged
    assert df1.loc[1, 'user_fail_rate'] == df2.loc[1, 'user_fail_rate']
