import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, GroupKFold

def get_p1_splits(df):
    """P1: random stratified split."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    return list(skf.split(df, df['is_redteam']))

def get_p2_splits(df):
    """P2: grouped by user."""
    gkf = GroupKFold(n_splits=5)
    return list(gkf.split(df, df['is_redteam'], groups=df['src_user']))

def get_p3_splits(df, purge_gap_days=7):
    """P3: single chronological split."""
    # Assuming df is sorted by time and has 'day' column
    max_day = df['day'].max()
    train_end = max_day // 2
    val_end = train_end + (max_day - train_end) // 2

    train_idx = df.index[df['day'] <= train_end].tolist()
    val_idx = df.index[(df['day'] > train_end + purge_gap_days) & (df['day'] <= val_end)].tolist()
    test_idx = df.index[df['day'] > val_end + purge_gap_days].tolist()

    return [(train_idx, val_idx, test_idx)]

def get_p4_splits(df, folds=4, purge_gap_days=7):
    """P4: rolling origin."""
    max_day = df['day'].max()
    splits = []
    step = max_day // (folds + 1)
    for i in range(1, folds + 1):
        train_end = i * step
        test_end = (i + 1) * step
        train_idx = df.index[df['day'] <= train_end].tolist()
        test_idx = df.index[(df['day'] > train_end + purge_gap_days) & (df['day'] <= test_end)].tolist()
        splits.append((train_idx, test_idx))
    return splits
