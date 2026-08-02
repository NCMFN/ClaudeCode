import os
import json
import pandas as pd
from datetime import timezone
from data_loaders.netlatency_loader import load_seattle_rtt_series
from model.fidelity import calculate_fidelity, T2_CONFIGS
from policy.adaptive_ttl import adaptive_ttl_policy
from policy.static_ttl import static_ttl_policy

def run_simulation(data_dir: str, output_dir: str, t2_key: str = 'aqt_ring', static_timeout: float = 0.1):
    os.makedirs(output_dir, exist_ok=True)
    t2 = T2_CONFIGS[t2_key]

    print(f"Running simulation with T2 = {t2}s ({t2_key}), static timeout = {static_timeout}s")

    # Load RTT time series
    rtt_series = load_seattle_rtt_series(data_dir)

    results = []
    telemetry = []

    for timestamp, rtt in rtt_series.items():
        if pd.isna(rtt):
            continue

        # Calculate true fidelity
        true_fidelity = calculate_fidelity(rtt, t2)

        # Policy decisions
        adaptive_action = adaptive_ttl_policy(rtt, t2)
        static_action = static_ttl_policy(rtt, static_timeout)

        # True states based on threshold (0.85)
        # Zombie Key Exposed: Fidelity < 0.85 but policy HOLDs
        # Unnecessary Flush: Fidelity >= 0.85 but policy FLUSHes
        is_zombie_adaptive = (true_fidelity < 0.85) and (adaptive_action == "HOLD")
        is_unnecessary_flush_adaptive = (true_fidelity >= 0.85) and (adaptive_action == "FLUSH")

        is_zombie_static = (true_fidelity < 0.85) and (static_action == "HOLD")
        is_unnecessary_flush_static = (true_fidelity >= 0.85) and (static_action == "FLUSH")

        results.append({
            'timestamp': timestamp.isoformat(),
            'rtt': rtt,
            'true_fidelity': true_fidelity,
            'adaptive_action': adaptive_action,
            'static_action': static_action,
            'zombie_adaptive': is_zombie_adaptive,
            'unnecessary_flush_adaptive': is_unnecessary_flush_adaptive,
            'zombie_static': is_zombie_static,
            'unnecessary_flush_static': is_unnecessary_flush_static
        })

        # Format for Open MCT Telemetry
        unix_ms = int(timestamp.timestamp() * 1000)
        telemetry.extend([
            {"timestamp": unix_ms, "value": rtt, "id": "net.rtt"},
            {"timestamp": unix_ms, "value": true_fidelity, "id": "qkd.fidelity"},
            {"timestamp": unix_ms, "value": 1 if adaptive_action == "FLUSH" else 0, "id": "policy.adaptive.flush"},
            {"timestamp": unix_ms, "value": 1 if static_action == "FLUSH" else 0, "id": "policy.static.flush"}
        ])

    # Convert to DataFrame
    df_results = pd.DataFrame(results)

    # Export CSV
    csv_path = os.path.join(output_dir, f'simulation_results_{t2_key}.csv')
    df_results.to_csv(csv_path, index=False)
    print(f"Results exported to {csv_path}")

    # Export JSON
    json_path = os.path.join(output_dir, f'telemetry_{t2_key}.json')
    with open(json_path, 'w') as f:
        json.dump(telemetry, f)
    print(f"Telemetry exported to {json_path}")

    return df_results

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, 'NetLatency-Data', 'Seattle')
    output_path = os.path.join(base_dir, 'outputs/raw')

    # We will simulate for both hardware regimes
    # For IonQ Aria, T2 = 1.0s. Let's use a static timeout of 0.3s (just for comparison)
    # For AQT ring, T2 = 0.05s. Let's use a static timeout of 0.02s
    run_simulation(data_path, output_path, t2_key='ionq_aria', static_timeout=0.3)
    run_simulation(data_path, output_path, t2_key='aqt_ring', static_timeout=0.02)
