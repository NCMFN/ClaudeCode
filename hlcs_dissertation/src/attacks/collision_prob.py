import numpy as np
import pandas as pd
import os

def collision_prob():
    # Zhandry bound ~ O(q_H^3 / 2^n)
    q_H = np.array([2**40, 2**64, 2**80, 2**100, 2**120], dtype=float)
    prob = (q_H ** 3) / (2 ** 256)

    df = pd.DataFrame({
        "q_H Queries": q_H,
        "Collision Probability": prob
    })

    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/collision_prob.csv'))
    df.to_csv(output_file, index=False)
    print("Hash collision probability under QROM complete.")

if __name__ == "__main__":
    collision_prob()
