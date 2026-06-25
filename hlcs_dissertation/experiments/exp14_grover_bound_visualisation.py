import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import security_analysis
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def run():
    print("Running Exp14: Quantum Attack Budget Visualisation")
    n_bits = np.linspace(128, 512, 100)

    # Cost in operations
    classical_ops = 2**n_bits
    grover_ops = 2**(n_bits / 2)

    # Adversary budget lines
    # Assuming 10^9 ops/sec
    tau_1ms = 1e-3 * 1e9 * 1e6 # Let's say parallel cores = 10^6
    tau_1yr = 365 * 24 * 3600 * 1e9 * 1e6

    # Create table data
    table_n = [128, 256, 384, 512]
    results = []
    for n in table_n:
        c_ops = 2.0**n
        g_ops = 2.0**(n/2)
        results.append({
            'n_bits': n,
            'classical_ops': c_ops,
            'grover_ops': g_ops,
            'quantum_secure_1ms': g_ops > tau_1ms
        })
    df = pd.DataFrame(results)
    df.to_csv('../tables/TABLE_20_Quantum_Security.csv', index=False)

    plt.figure(figsize=(10, 6))
    plt.plot(n_bits, classical_ops, label='Classical Attack (2^n)', color="#1F4E79")
    plt.plot(n_bits, grover_ops, label='Quantum Attack (2^{n/2})', color="#A23B72")
    plt.axhline(tau_1ms, color='red', linestyle='--', label='Adv. Budget: τ = 1ms')
    plt.axhline(tau_1yr, color='orange', linestyle='--', label='Adv. Budget: τ = 1 year')
    plt.yscale('log')
    plt.xlabel('Hash Output Size (bits)')
    plt.ylabel('Cost (Operations)')
    plt.title('Figure 23: Quantum Attack Costs vs Hash Size')
    plt.legend()
    plt.savefig('../figures/fig23_quantum_attack_costs.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig23_quantum_attack_costs.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig23_quantum_attack_costs.txt', 'w') as f:
        f.write("Figure 23: Log-scale plot of classical and quantum attack costs vs. hash output size, superimposed with adversary operation budgets.")

    print("Exp14 completed.")
    return 1, 1

if __name__ == '__main__':
    run()
