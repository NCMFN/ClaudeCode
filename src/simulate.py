import json
import csv
import pandas as pd
from tqdm import tqdm

from src.data_loaders.netlatency_loader import load_seattle_data
from src.model.fidelity import compute_fidelity, T2_REGIMES
from src.policy.adaptive_ttl import AdaptiveTTLPolicy
from src.policy.static_ttl import StaticTTLPolicy

def run_simulation():
    print("Loading RTT data...")
    # Load just a subset for simulation speed? The dataset is 6M rows.
    # To have reasonable output files and execution time, let's use the first 10,000 samples.
    rtt_series = load_seattle_data(sampling_interval_ms=10) # 100 Hz simulation
    rtt_series = rtt_series.head(10000)

    # Policies
    adaptive_policy = AdaptiveTTLPolicy(threshold=0.85)

    # Choose static TTLs based on a naive heuristic: e.g. 0.05s timeout
    # Or something comparable to the expected RTT.
    # Let's just use 0.1s for IonQ and 0.01s for AQT
    static_policies = {
        'IonQ_Aria': StaticTTLPolicy(timeout_seconds=0.1),
        'AQT': StaticTTLPolicy(timeout_seconds=0.01)
    }

    results = []
    telemetry_json = []

    print("Running simulations...")
    for regime_name, t2 in T2_REGIMES.items():
        static_policy = static_policies[regime_name]

        # We need to simulate both policies on this regime
        for policy_name, policy in [('Adaptive', adaptive_policy), ('Static', static_policy)]:
            for timestamp, rtt in tqdm(rtt_series.items(), total=len(rtt_series), desc=f"{policy_name}-{regime_name}"):

                fidelity = compute_fidelity(rtt, t2)
                action = policy.evaluate(rtt, t2)

                # Append to results
                row = {
                    'timestamp': timestamp.isoformat(),
                    'rtt_seconds': rtt,
                    't2_regime': regime_name,
                    't2_value': t2,
                    'policy': policy_name,
                    'fidelity': fidelity,
                    'action': action
                }
                results.append(row)

                # Open MCT telemetry JSON schema: { timestamp, value, id }
                # We emit one for fidelity and one for rtt
                tel_id_prefix = f"telemetry.{regime_name}.{policy_name}"
                telemetry_json.append({
                    "timestamp": timestamp.timestamp() * 1000, # ms since epoch
                    "value": fidelity,
                    "id": f"{tel_id_prefix}.fidelity"
                })
                telemetry_json.append({
                    "timestamp": timestamp.timestamp() * 1000,
                    "value": rtt,
                    "id": f"{tel_id_prefix}.rtt"
                })

    # Save CSV
    print("Saving CSV output...")
    csv_file = "/app/src/outputs/raw/simulation_results.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    # Save JSON
    print("Saving JSON telemetry output...")
    json_file = "/app/src/outputs/raw/open_mct_telemetry.json"
    with open(json_file, 'w') as f:
        json.dump(telemetry_json, f)

    print(f"Simulation complete. Generated {len(results)} rows.")

if __name__ == '__main__':
    run_simulation()
