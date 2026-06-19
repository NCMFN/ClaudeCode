import numpy as np
import pandas as pd
import os

def bkz_cost():
    n_lat = np.arange(64, 1025, 16)
    cost = 2 ** (0.292 * n_lat)

    df = pd.DataFrame({
        "Lattice Dimension": n_lat,
        "BKZ Cost (Gates)": cost
    })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/bkz_cost.csv'))
    df.to_csv(output_file, index=False)
    print("BKZ attack cost estimation complete.")

if __name__ == "__main__":
    bkz_cost()
