import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_p3_no_overlap():
    from src.protocols import get_p3_splits
    import pandas as pd
    df = pd.DataFrame({"day": list(range(60)), "is_redteam": [0]*60, "src_user": ["U1"]*60})
    splits = get_p3_splits(df)
    train, val, test = splits[0]
    assert len(set(train).intersection(val)) == 0
    assert len(set(val).intersection(test)) == 0
    assert len(set(train).intersection(test)) == 0
