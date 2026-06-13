import sys
import os
import time
import pandas as pd
from tqdm import tqdm

# Add parent dir to path to import src and config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from src.drpp_protocol import DRPPProtocol
from src.prf_simulator import generate_secret
from src.traditional_auth import TraditionalAuth
from src.collusion_attack import CollusionAttack
from src.security_game import compute_advantage

def run_experiments():
    k_values = config.K_VALUES
    n_trials = config.N_TRIALS

    results = []
    start_time = time.time()

    print(f"Running experiments with {n_trials} trials per configuration...")

    # 1. DRPP Protocol Simulation
    for k in tqdm(k_values, desc="DRPP Simulation"):
        secret = generate_secret(k)
        protocol = DRPPProtocol(k, secret)

        successes = 0
        for _ in range(n_trials):
            # Prover is absent (False), forcing random guessing through the compute logic
            run_data = protocol.run_protocol(prover_present=False)
            if run_data["outcome"]:
                successes += 1

        success_rate = successes / n_trials
        results.append({
            "k": k,
            "model": "DRPP",
            "success_rate": success_rate,
            "n_trials": n_trials
        })

    # 2. Traditional Auth
    trad_auth = TraditionalAuth(random_seed=config.RANDOM_SEED)
    for k in tqdm(k_values, desc="Traditional Auth"):
        res = trad_auth.simulate(n_trials)
        results.append({
            "k": k,
            "model": "Traditional",
            "success_rate": res["success_rate"],
            "n_trials": n_trials
        })

    # 3. Collusion Attack
    for k in tqdm(k_values, desc="Collusion Attack"):
        attack = CollusionAttack(k, n_guesses_per_challenge=1)
        res = attack.simulate(n_trials)
        results.append({
            "k": k,
            "model": "Collusion",
            "success_rate": res["success_rate"],
            "n_trials": n_trials
        })

    # Save raw results
    os.makedirs(os.path.join(config.OUTPUT_DIR, "results"), exist_ok=True)
    df_results = pd.DataFrame(results)
    df_results.to_csv(os.path.join(config.OUTPUT_DIR, "results", "raw_results.csv"), index=False)

    # Run Security Game Validation
    print("Running Security Game Validation...")
    sec_df = compute_advantage(k_values, n_trials)
    sec_df.to_csv(os.path.join(config.OUTPUT_DIR, "results", "security_game_results.csv"), index=False)

    end_time = time.time()
    print(f"Experiments completed in {end_time - start_time:.2f} seconds.")

    # Print summary table
    print("\nSummary Table I - Attack Success Probability (%)")
    print("-" * 60)
    print(f"{'Challenge Bits (k)':<20} | {'DRPP':<10} | {'Collusion':<10} | {'Traditional':<10}")
    print("-" * 60)

    for k in k_values:
        drpp_val = df_results[(df_results["k"] == k) & (df_results["model"] == "DRPP")]["success_rate"].values[0]
        col_val = df_results[(df_results["k"] == k) & (df_results["model"] == "Collusion")]["success_rate"].values[0]
        trad_val = df_results[(df_results["k"] == k) & (df_results["model"] == "Traditional")]["success_rate"].values[0]

        drpp_str = f"{drpp_val*100:.4f}%" if pd.notna(drpp_val) else "-"
        col_str = f"{col_val*100:.2f}%" if pd.notna(col_val) else "-"
        trad_str = f"{trad_val*100:.2f}%" if pd.notna(trad_val) else "-"

        print(f"{k:<20} | {drpp_str:<10} | {col_str:<10} | {trad_str:<10}")

if __name__ == "__main__":
    run_experiments()
