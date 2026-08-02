import pandas as pd
import yaml
from data_ingest import ingest_data
from dbs_policy import get_block_size_dbs, get_block_size_fixed_large, get_block_size_fixed_small
from qber_synth import generate_qber_series
from key_rate import compute_skr_per_block

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def compute_t2k(block_size, rtt_ms, config):
    c1 = config["c1"]
    c2 = config["c2"]
    return c1 * block_size + c2 * rtt_ms

def simulate(rtt_series, config):
    num_blocks = len(rtt_series)
    qber_series = generate_qber_series(num_blocks, config)

    results = []

    for i in range(num_blocks):
        rtt = rtt_series[i]
        qber = qber_series[i]

        N_dbs = get_block_size_dbs(rtt, config)
        skr_dbs = compute_skr_per_block(N_dbs, qber, config)
        t2k_dbs = compute_t2k(N_dbs, rtt, config)

        N_large = get_block_size_fixed_large(rtt, config)
        skr_large = compute_skr_per_block(N_large, qber, config)
        t2k_large = compute_t2k(N_large, rtt, config)

        N_small = get_block_size_fixed_small(rtt, config)
        skr_small = compute_skr_per_block(N_small, qber, config)
        t2k_small = compute_t2k(N_small, rtt, config)

        results.append({
            "block_id": i,
            "rtt_ms": rtt,
            "qber": qber,
            "N_dbs": N_dbs,
            "skr_dbs": skr_dbs,
            "t2k_dbs": t2k_dbs,
            "N_large": N_large,
            "skr_large": skr_large,
            "t2k_large": t2k_large,
            "N_small": N_small,
            "skr_small": skr_small,
            "t2k_small": t2k_small
        })

    return pd.DataFrame(results)
