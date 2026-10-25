import pandas as pd
import numpy as np
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# To prevent OOM/slowdown over 1 billion events, we bound our state tracking.
MAX_TRACKED_USERS = 500_000

class BoundedState:
    def __init__(self, max_keys=MAX_TRACKED_USERS):
        self.counts = {}
        self.comps = {}
        self.max_keys = max_keys

    def reset(self):
        self.counts.clear()
        self.comps.clear()

_state = BoundedState()

def reset_feature_state():
    _state.reset()

def update_global_states_and_compute(df: pd.DataFrame, train_cutoff_time: int = None) -> pd.DataFrame:
    """
    Computes causal features using fully vectorized pandas operations combined with global dictionary mappings.
    """
    df = df.copy()
    if 'time' not in df.columns or df.empty:
         return df

    df['hour'] = (df['time'] % 86400) // 3600
    df['day_of_week'] = df['day'] % 7 if 'day' in df.columns else (df['time'] // 86400) % 7

    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

    # Fast grouped tracking within the chunk
    # 1. user_event_count: existing global count + cumulative count within chunk
    # Map the current global count to each user first
    global_user_counts = df['src_user'].map(_state.counts).fillna(0).astype(int)

    # Calculate cumulative count for this user WITHIN this specific chunk
    chunk_cumcount = df.groupby('src_user').cumcount()

    # Total count right before this event occurred
    df['user_event_count'] = global_user_counts + chunk_cumcount

    # Update global counts dictionary with the total events in this chunk
    chunk_totals = df['src_user'].value_counts()
    for user, count in chunk_totals.items():
        if len(_state.counts) < _state.max_keys or user in _state.counts:
            _state.counts[user] = _state.counts.get(user, 0) + count

    # 2. user_train_unique_comps: tracking peer stats before cutoff
    if train_cutoff_time is None:
        # If train_cutoff is None, we treat the entire dataset as test-time (frozen)
        # based on user requirement to "freeze after training window". If they pass None,
        # they mean "don't learn any new graphs" or "learn all". For safety, let's learn all if None.
        is_train = pd.Series([True]*len(df), index=df.index)
    else:
        is_train = df['time'] < train_cutoff_time

    train_df = df[is_train]

    # Update global peer stats with new unique computers accessed in the training portion of this chunk
    if not train_df.empty:
        new_comps = train_df.groupby('src_user')['dst_comp'].unique()
        for user, comps in new_comps.items():
            if len(_state.comps) < _state.max_keys or user in _state.comps:
                if user not in _state.comps:
                    _state.comps[user] = set()
                _state.comps[user].update(comps)

    # Now map the updated sizes to the full chunk
    df['user_train_unique_comps'] = df['src_user'].map(lambda u: len(_state.comps.get(u, set())))

    return df

def finalize_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cat_cols = ['auth_type', 'logon_type', 'auth_orientation', 'success']
    for col in cat_cols:
        if col in df.columns:
            df[f'{col}_encoded'], _ = pd.factorize(df[col])
    return df

def get_feature_columns() -> List[str]:
    return [
        'hour_sin', 'hour_cos', 'day_of_week',
        'user_event_count', 'user_train_unique_comps',
        'auth_type_encoded', 'logon_type_encoded',
        'auth_orientation_encoded', 'success_encoded'
    ]
