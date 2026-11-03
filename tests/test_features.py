def test_causality():
    import pandas as pd
    df = pd.DataFrame({"src_user": ["A", "B", "A", "A"]})
    df['user_login_count'] = df.groupby('src_user').cumcount() + 1
    assert df['user_login_count'].tolist() == [1, 1, 2, 3]
