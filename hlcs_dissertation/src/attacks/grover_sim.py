import numpy as np
import pandas as pd
import os

def grover_cost():
    n_bits = np.arange(64, 513, 8)
    cost = 2 ** (n_bits / 2)

    df = pd.DataFrame({
        "Hash Size (bits)": n_bits,
        "Grover Cost": cost
    })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/grover_cost.csv'))
    df.to_csv(output_file, index=False)
    print("Grover attack simulation complete.")

if __name__ == "__main__":
    grover_cost()
