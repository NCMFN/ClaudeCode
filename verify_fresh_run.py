import pandas as pd
import glob

def check_diff():
    # Verify outputs actually changed
    old_ablation = pd.read_csv("outputs/tables/_pass3_snapshot/ablation_study.csv")
    new_ablation = pd.read_csv("outputs/tables/ablation_study.csv")
    print("Ablation Match:", old_ablation.equals(new_ablation))
    if not old_ablation.equals(new_ablation):
        print("Diff: Ablation rows changed from", len(old_ablation), "to", len(new_ablation))

    old_adv = pd.read_csv("outputs/tables/_pass3_snapshot/adversarial_robustness.csv")
    new_adv = pd.read_csv("outputs/tables/adversarial_robustness.csv")
    print("Adversarial Match:", old_adv.equals(new_adv))
    if not old_adv.equals(new_adv):
        print("Diff: Values changed.", new_adv.head())

if __name__ == "__main__":
    check_diff()
