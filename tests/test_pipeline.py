import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from features import update_global_states_and_compute, reset_feature_state
from protocols import p3_chronological_split
from figure_lint import FORBIDDEN_WORDS

def test_causal_feature_leakage():
    reset_feature_state()
    df = pd.DataFrame({
        'time': [100, 200, 300],
        'day': [0, 0, 0],
        'src_user': ['u1', 'u1', 'u2'],
        'dst_comp': ['c1', 'c2', 'c3'],
        'auth_type': ['a', 'a', 'b'],
        'logon_type': ['l1', 'l1', 'l2'],
        'auth_orientation': ['o1', 'o1', 'o2'],
        'success': ['s', 's', 'f']
    })

    feat1 = update_global_states_and_compute(df)

    reset_feature_state()
    df_shuffled = df.copy()
    df_shuffled.iloc[1], df_shuffled.iloc[2] = df_shuffled.iloc[2].copy(), df_shuffled.iloc[1].copy()

    feat2 = update_global_states_and_compute(df_shuffled)

    pd.testing.assert_series_equal(
        feat1[feat1['time'] == 100].iloc[0],
        feat2[feat2['time'] == 100].iloc[0]
    )

def test_chronological_split_purge_gap():
    df = pd.DataFrame({
        'time': [0, 86400 * 5, 86400 * 15, 86400 * 25, 86400 * 35],
        'day': [0, 5, 15, 25, 35],
        'is_malicious': [0, 0, 1, 0, 1]
    })

    train_days, val_days, test_days, purge_gap = 10, 0, 10, 7
    gen = p3_chronological_split(df, train_days, val_days, test_days, purge_gap)

    train_idx, test_idx = next(gen)

    train_days_arr = df.iloc[train_idx]['day'].values
    test_days_arr = df.iloc[test_idx]['day'].values

    if len(train_days_arr) > 0 and len(test_days_arr) > 0:
        max_train = train_days_arr.max()
        min_test = test_days_arr.min()
        assert min_test - max_train >= purge_gap

def test_no_verify_false():
    src_dir = os.path.join(os.path.dirname(__file__), '../src')
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as file:
                    content = file.read()
                    assert "verify=False" not in content, f"verify=False found in {f}"
                    assert "verify = False" not in content, f"verify=False found in {f}"

def test_no_random_assignment():
    src_dir = os.path.join(os.path.dirname(__file__), '../src')
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f == 'evaluate.py':
                continue
            if f.endswith('.py'):
                with open(os.path.join(root, f), 'r') as file:
                    content = file.read()
                    assert "random.choice" not in content, f"random.choice found in {f}"

def test_forbidden_words_in_paper():
    paper_dir = os.path.join(os.path.dirname(__file__), '../paper_revision')
    for root, _, files in os.walk(paper_dir):
        for f in files:
            if f == 'CHANGES.md':
                continue
            if f.endswith('.tex') or f.endswith('.md'):
                with open(os.path.join(root, f), 'r') as file:
                    content = file.read().lower()
                    for word in FORBIDDEN_WORDS:
                        assert word not in content, f"Forbidden word '{word}' found in {f}"
