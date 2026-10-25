import pytest
import pandas as pd
import numpy as np
import os
import sys
import resource
import tempfile
import gc
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from evaluate import compute_paired_delta_ci
from ingest import ingest_auth_data
from features import update_global_states_and_compute, reset_feature_state

def test_paired_delta_ci():
    y_true = pd.Series([1, 0, 1, 0, 1] * 20)
    y_score_p1 = pd.Series([1, 0, 1, 0, 1] * 20)
    y_score_p3 = pd.Series([0, 1, 0, 1, 0] * 20)
    group_ids = pd.Series([i // 5 for i in range(100)])

    ci_low, ci_high = compute_paired_delta_ci(y_true, y_score_p1, y_score_p3, group_ids, n_bootstraps=10)
    assert ci_low >= 0
    assert ci_high >= 0
    assert ci_low <= ci_high

def test_memory_limit_sampling_subprocess():
    # Use a subprocess to accurately measure max RSS scaling
    code = """
import sys
import pandas as pd
import numpy as np
import resource
import sampling

def mock_stream():
    for _ in range(20):
        yield pd.DataFrame({
            'time': [1]*10000,
            'src_user': ['u1']*10000,
            'src_comp': ['c1']*10000,
            'dst_comp': ['c2']*10000,
            'is_malicious': [0]*10000,
            'day': [0]*10000
        })

df, prev, counts = sampling.time_stratified_sample_stream(mock_stream(), 5, 10)
sys.stdout.write(str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py') as f:
        f.write(code)
        f.flush()

        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))

        res = subprocess.run([sys.executable, f.name], capture_output=True, text=True, env=env)
        assert res.returncode == 0
        peak_rss = int(res.stdout.strip())

        # In Linux, ru_maxrss is in KB. 350,000 KB = 350 MB.
        assert peak_rss < 350000

def test_feature_immutability():
    reset_feature_state()
    df_past = pd.DataFrame({
        'time': [100, 200],
        'src_user': ['u1', 'u1'],
        'src_comp': ['c1', 'c1'],
        'dst_comp': ['c2', 'c2'],
        'day': [0, 0]
    })

    feat_past_1 = update_global_states_and_compute(df_past, train_cutoff_time=1000)

    df_future = pd.DataFrame({
        'time': [300, 400],
        'src_user': ['u99', 'u99'],
        'src_comp': ['c99', 'c99'],
        'dst_comp': ['c99', 'c99'],
        'day': [0, 0]
    })
    _ = update_global_states_and_compute(df_future, train_cutoff_time=1000)

    assert feat_past_1.iloc[0]['user_event_count'] == 0
    assert feat_past_1.iloc[1]['user_event_count'] == 1

def test_unmatched_redteam_logging():
    with tempfile.TemporaryDirectory() as td:
        auth_file = os.path.join(td, 'auth.txt.gz')
        import gzip
        with gzip.open(auth_file, 'wt') as f:
            f.write("100,U1@DOM,U2@DOM,C1,C1,Auth,Logon,Orient,Success\n")

        redteam_set = {
            (100, 'u1@dom', 'C1', 'C1'),
            (100, 'u3@dom', 'C1', 'C1'),
            (200, 'u1@dom', 'C1', 'C1'),
        }

        _, _, unmatched_reasons = ingest_auth_data(auth_file, redteam_set, td)
        assert (200, 'u1@dom', 'C1', 'C1') in unmatched_reasons
        assert unmatched_reasons[(200, 'u1@dom', 'C1', 'C1')] == 'no_auth_at_timestamp'
        assert (100, 'u3@dom', 'C1', 'C1') in unmatched_reasons
        assert unmatched_reasons[(100, 'u3@dom', 'C1', 'C1')] == 'time_match_user_mismatch'
