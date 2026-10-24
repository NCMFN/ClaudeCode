import os
import sys
import csv
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from config import SEED, PURGE_GAP_SECONDS, MIN_POSITIVES_PER_TEST_FOLD

def leakage_check(train_idx, test_idx, df, split_name):
    if len(train_idx) == 0 or len(test_idx) == 0:
        return

    train_max_t = df.iloc[train_idx]['time'].max()
    test_min_t = df.iloc[test_idx]['time'].min()

    if split_name in ['chronological_holdout', 'rolling_origin']:
        assert train_max_t < test_min_t, f"Leakage detected in {split_name}: train_max_t ({train_max_t}) >= test_min_t ({test_min_t})"

def split_random_row(df):
    """ Deliberately leaky reference """
    np.random.seed(SEED)
    idx = np.random.permutation(len(df))
    split_point = int(0.8 * len(df))
    return [(idx[:split_point], idx[split_point:])]

def split_random_user_group(df):
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    return list(gss.split(df, groups=df['user']))

def split_chronological_holdout(df):
    df_sorted = df.sort_values('time')
    split_point = int(0.8 * len(df_sorted))
    train_end_time = df_sorted.iloc[split_point]['time']

    train_idx = np.where(df['time'] <= train_end_time)[0]
    test_idx = np.where(df['time'] > train_end_time + PURGE_GAP_SECONDS)[0]
    return [(train_idx, test_idx)]

def split_rolling_origin(df):
    df_sorted = df.sort_values('time')
    day_indices = df_sorted['day_index'].unique()

    folds = []
    # e.g., train on days 0..k, test on day k+2 (to account for purge gap)
    if len(day_indices) > 5:
        # Simplistic rolling origin
        for i in range(len(day_indices) // 2, len(day_indices) - 2):
            train_end_day = day_indices[i]
            train_idx = np.where(df['day_index'] <= train_end_day)[0]
            train_end_time = df.iloc[train_idx]['time'].max()
            test_idx = np.where(df['time'] > train_end_time + PURGE_GAP_SECONDS)[0]
            if len(test_idx) > 0:
                folds.append((train_idx, test_idx))
    else:
        # Fallback if too few days
        folds = split_chronological_holdout(df)

    return folds

def save_split_composition(df, split_name, folds):
    os.makedirs("outputs/tables", exist_ok=True)
    file_exists = os.path.exists("outputs/tables/split_composition.csv")

    with open("outputs/tables/split_composition.csv", "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["split_strategy", "fold_idx", "train_pos", "train_neg", "test_pos", "test_neg", "status"])

        for idx, (train_idx, test_idx) in enumerate(folds):
            train_pos = df.iloc[train_idx]['label'].sum()
            train_neg = len(train_idx) - train_pos
            test_pos = df.iloc[test_idx]['label'].sum()
            test_neg = len(test_idx) - test_pos

            status = "OK" if test_pos >= MIN_POSITIVES_PER_TEST_FOLD else "UNDERPOWERED"
            writer.writerow([split_name, idx, train_pos, train_neg, test_pos, test_neg, status])

def generate_splits(df):
    splits = {
        'random_row': split_random_row(df),
        'random_user_group': split_random_user_group(df),
        'chronological_holdout': split_chronological_holdout(df),
        'rolling_origin': split_rolling_origin(df)
    }

    for split_name, folds in splits.items():
        save_split_composition(df, split_name, folds)
        for fold_idx, (train_idx, test_idx) in enumerate(folds):
            leakage_check(train_idx, test_idx, df, split_name)

    return splits
