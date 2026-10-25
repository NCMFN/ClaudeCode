import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, GroupShuffleSplit
import logging
from typing import Iterator, Tuple

logger = logging.getLogger(__name__)

def p1_random_split(df: pd.DataFrame, n_splits=5, seed=42) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    """P1: Random stratified split (naive literature baseline). Leakage prone."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    return skf.split(df, df['is_malicious'])

def p2_user_split(df: pd.DataFrame, test_size=0.2, seed=42) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    """P2: Grouped by user. Prevents user leakage, but still time-leaky."""
    gss = GroupShuffleSplit(n_splits=5, test_size=test_size, random_state=seed)
    return gss.split(df, df['is_malicious'], groups=df['src_user'])

def p3_chronological_split(df: pd.DataFrame, train_days: int, val_days: int, test_days: int, purge_gap_days: int) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    """
    P3: Single chronological split.
    Earliest days train, purge gap, next block validate, latest block test.
    For simplicity, returns just train and test indices here. (Validation can be carved from train if needed).
    """
    df_sorted = df.sort_values('time').reset_index(drop=True)
    start_day = df_sorted['day'].min()

    train_end = start_day + train_days
    test_start = train_end + purge_gap_days
    test_end = test_start + test_days

    train_idx = df_sorted[(df_sorted['day'] >= start_day) & (df_sorted['day'] < train_end)].index.values
    test_idx = df_sorted[(df_sorted['day'] >= test_start) & (df_sorted['day'] < test_end)].index.values

    yield train_idx, test_idx

def p4_rolling_origin(df: pd.DataFrame, n_splits: int, purge_gap_days: int) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
    """
    P4: Rolling origin chronological evaluation with purge gap.
    Divides timeline into chunks. Train expands, test shifts forward.
    """
    df_sorted = df.sort_values('time').reset_index(drop=True)
    min_day = df_sorted['day'].min()
    max_day = df_sorted['day'].max()
    total_days = max_day - min_day + 1

    # Simple block sizing
    block_size = int(total_days / (n_splits + 1))
    if block_size < 1:
        logger.warning("Timeline too short for requested number of splits. Defaulting to 1 split.")
        block_size = total_days // 2
        n_splits = 1

    for i in range(1, n_splits + 1):
        train_end = min_day + i * block_size
        test_start = train_end + purge_gap_days
        test_end = test_start + block_size

        train_idx = df_sorted[df_sorted['day'] < train_end].index.values
        test_idx = df_sorted[(df_sorted['day'] >= test_start) & (df_sorted['day'] < test_end)].index.values

        yield train_idx, test_idx
