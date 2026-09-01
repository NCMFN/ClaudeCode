import pandas as pd
import os

def display():
    manifest_path = "outputs/paper_assets/paper_assets_manifest.csv"
    if not os.path.exists(manifest_path):
        print("Run the pipeline first.")
        return

    print("\n--- Evaluation Metrics ---")
    metrics = pd.read_csv("outputs/tables/evaluation_metrics.csv")
    print(metrics.to_string(index=False))

    print("\n--- Adversarial Robustness ---")
    if os.path.exists("outputs/tables/adversarial_robustness.csv"):
        adv = pd.read_csv("outputs/tables/adversarial_robustness.csv")
        print(adv.to_string(index=False))

    print("\n--- Methodology Comparison ---")
    method = pd.read_csv("outputs/tables/methodology_comparison.csv")
    print(method.to_string(index=False))

if __name__ == "__main__":
    display()
