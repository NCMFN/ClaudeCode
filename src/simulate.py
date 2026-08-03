import json
import os
import pandas as pd
from src.dbs_policy import load_config, dbs_policy, fixed_large_policy, fixed_small_policy
from src.key_rate import compute_secure_key_rate
from src.qber_synth import generate_qber_series

def compute_t2k(block_size, rtt_ms, config):
    """
    Time-to-Key (T2K) model: c1 * block_size + c2 * rtt
    Constants c1, c2 in config are illustrative.
    """
    c1 = config.get("c1", 0.001)
    c2 = config.get("c2", 0.5)
    return c1 * block_size + c2 * rtt_ms

def simulate_policy(name, policy_fn, rtt_trace, qber_trace, config):
    results = []

    for i, row in rtt_trace.iterrows():
        rtt_ms = row["rtt_ms"]
        timestamp = row["timestamp"]
        qber = qber_trace[i]

        block_size = policy_fn(rtt_ms, config)
        skr = compute_secure_key_rate(block_size, qber, config)
        t2k = compute_t2k(block_size, rtt_ms, config)

        failure = 1 if skr == 0.0 else 0

        results.append({
            "block_index": i,
            "timestamp": timestamp,
            "rtt_ms": float(rtt_ms),
            "qber": float(qber),
            "block_size": int(block_size),
            "skr": float(skr),
            "t2k": float(t2k),
            "failure": failure
        })
    return results

def main():
    config = load_config()

    rtt_df = pd.read_csv("data/rtt_time_series.csv")
    num_blocks = len(rtt_df)

    qber_trace = generate_qber_series(num_blocks, config)

    print("Simulating DBS Policy...")
    dbs_results = simulate_policy("dbs", dbs_policy, rtt_df, qber_trace, config)

    print("Simulating Fixed Large Policy...")
    large_results = simulate_policy("fixed_large", fixed_large_policy, rtt_df, qber_trace, config)

    print("Simulating Fixed Small Policy...")
    small_results = simulate_policy("fixed_small", fixed_small_policy, rtt_df, qber_trace, config)

    all_results = {
        "dbs": dbs_results,
        "fixed_large": large_results,
        "fixed_small": small_results
    }

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results.json", "w") as f:
        json.dump(all_results, f)

    print("Simulation complete. Results saved to outputs/results.json.")

if __name__ == "__main__":
    main()
