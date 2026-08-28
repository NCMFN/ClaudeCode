import pandas as pd
import numpy as np
import os
import shutil

def run_test():
    res1 = pd.read_csv('results/model_comparison.csv')
    # Backup
    shutil.copy('results/model_comparison.csv', 'results/model_comparison_run1.csv')

    # Run again
    os.system('python3 scripts/03_model_training.py > /dev/null 2>&1')

    res2 = pd.read_csv('results/model_comparison.csv')
    shutil.copy('results/model_comparison.csv', 'results/model_comparison_run2.csv')

    # Diff check (excluding latency as it naturally varies)
    cols_to_check = ['model', 'fold', 'f1', 'roc_auc', 'recall_0', 'recall_1', 'recall_2', 'recall_3']

    try:
        if res1[cols_to_check].equals(res2[cols_to_check]) or np.allclose(res1[cols_to_check].select_dtypes(include=np.number).fillna(0), res2[cols_to_check].select_dtypes(include=np.number).fillna(0)):
            with open('outputs/reproducibility_diff.txt', 'w') as f:
                f.write("0")
            print("Models are deterministic.")
        else:
            with open('outputs/reproducibility_diff.txt', 'w') as f:
                f.write("1")
            print("Models are NOT deterministic!")
    except Exception as e:
        with open('outputs/reproducibility_diff.txt', 'w') as f:
            f.write("1")
        print(f"Error diffing: {e}")

os.makedirs("outputs", exist_ok=True)
run_test()
