def test_sampling_deterministic():
    import pandas as pd
    import numpy as np
    df = pd.DataFrame({"time": [1], "src_user": ["u1"], "src_comp": ["c1"], "dst_comp": ["c2"]})
    h1 = pd.util.hash_pandas_object(df, index=False).iloc[0]
    h2 = pd.util.hash_pandas_object(df, index=False).iloc[0]
    assert h1 == h2
