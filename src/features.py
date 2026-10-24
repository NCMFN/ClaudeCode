import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def build_features(df, train_idx=None, use_temporal=True):
    """
    Build features ensuring no hindsight.
    If train_idx is provided, we compute group statistics (peer groups, scalers) ONLY on train.
    """

    df = df.copy()
    df['orig_idx'] = np.arange(len(df))
    df = df.sort_values('time')

    # Cast potential int cols to float to avoid pandas casting errors during scaling

    df['user_event_count'] = df.groupby('user').cumcount().astype(float)
    df['src_comp_distinct'] = df.groupby('user')['src_comp'].transform(lambda x: (~x.duplicated()).cumsum()).astype(float)

    df['is_fail'] = (df['success'] == 'Fail').astype(int)
    df['user_fail_count'] = df.groupby('user')['is_fail'].cumsum() - df['is_fail']
    df['user_fail_rate'] = (df['user_fail_count'] / np.maximum(1, df['user_event_count'])).astype(float)

    df['first_time_host'] = (~df.duplicated(subset=['user', 'src_comp'])).astype(float)

    if use_temporal:
        df['hour_cos'] = np.cos(2 * np.pi * df['second_of_day'] / 86400).astype(float)
        df['hour_sin'] = np.sin(2 * np.pi * df['second_of_day'] / 86400).astype(float)
    else:
        df['hour_cos'] = 0.0
        df['hour_sin'] = 0.0

    freq_cols = ['auth_type', 'logon_type', 'orientation']
    for col in freq_cols:
        if train_idx is not None:
            train_df = df.loc[train_idx]
            freqs = train_df[col].value_counts(normalize=True).to_dict()
        else:
            freqs = df[col].value_counts(normalize=True).to_dict()
        df[f'{col}_freq'] = df[col].map(freqs).fillna(0.0).astype(float)

    if train_idx is not None:
        train_df = df.loc[train_idx]
        user_stats = train_df.groupby('user').agg({
            'is_fail': 'mean',
            'src_comp': 'nunique',
            'orig_idx': 'count'
        })
        user_stats['peer_group'] = pd.qcut(user_stats['orig_idx'], q=3, labels=False, duplicates='drop')
        peer_mapping = user_stats['peer_group'].to_dict()
        df['peer_group'] = df['user'].map(peer_mapping).fillna(0)

        train_df_w_peer = train_df.copy()
        train_df_w_peer['peer_group'] = train_df_w_peer['user'].map(peer_mapping).fillna(0)
        peer_stats = train_df_w_peer.groupby('peer_group')['user_event_count'].agg(['mean', 'std'])

        def zscore_peer(row):
            pg = row['peer_group']
            val = row['user_event_count']
            if pg in peer_stats.index:
                m = peer_stats.loc[pg, 'mean']
                s = peer_stats.loc[pg, 'std']
                if s > 0:
                    return (val - m) / s
            return 0.0

        df['peer_zscore'] = df.apply(zscore_peer, axis=1).astype(float)
    else:
        df['peer_group'] = 0
        df['peer_zscore'] = 0.0

    df['host_degree'] = df.groupby('src_comp').cumcount().astype(float)

    auth_types = df['auth_type'].unique()
    auth_map = {v: i+1 for i, v in enumerate(auth_types)}
    df['auth_code'] = df['auth_type'].map(auth_map)

    def build_seqs(group):
        codes = group['auth_code'].values
        seqs = []
        for i in range(len(codes)):
            start = max(0, i-9)
            seq = list(codes[start:i+1])
            if len(seq) < 10:
                seq = [0]*(10-len(seq)) + seq
            seqs.append(seq)
        group['seq'] = seqs
        return group

    df = df.groupby('user', group_keys=False).apply(build_seqs)
    df = df.sort_values('orig_idx').reset_index(drop=True)

    feature_cols = [
        'user_event_count', 'src_comp_distinct', 'user_fail_rate',
        'first_time_host', 'hour_cos', 'hour_sin',
        'auth_type_freq', 'logon_type_freq', 'orientation_freq',
        'peer_zscore', 'host_degree'
    ]

    # Pre-cast feature columns to float to avoid SettingWithCopy and LossySetitem Error
    for c in feature_cols:
        df[c] = df[c].astype(float)

    if train_idx is not None:
        scaler = StandardScaler()
        df.loc[train_idx, feature_cols] = scaler.fit_transform(df.loc[train_idx, feature_cols])
        test_idx = list(set(df.index) - set(train_idx))
        if test_idx:
            df.loc[test_idx, feature_cols] = scaler.transform(df.loc[test_idx, feature_cols])

    return df, feature_cols

def extract_X_y(df, feature_cols):
    X = df[feature_cols].values
    y = df['label'].values
    X_seq = np.stack(df['seq'].values)
    return X, X_seq, y
