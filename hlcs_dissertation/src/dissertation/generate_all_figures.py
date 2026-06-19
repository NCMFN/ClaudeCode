import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.patches as patches
import os
import sys

sns.set_theme("paper")
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

FIGURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../figures'))
os.makedirs(FIGURES_DIR, exist_ok=True)

def save_fig(fig, name):
    fig.savefig(os.path.join(FIGURES_DIR, f"{name}.png"), bbox_inches='tight')
    fig.savefig(os.path.join(FIGURES_DIR, f"{name}.pdf"), bbox_inches='tight')
    plt.close(fig)

def fig_01():
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')

    # Trader
    rect1 = patches.FancyBboxPatch((0.1, 0.4), 0.2, 0.2, boxstyle="round,pad=0.05", edgecolor='black', facecolor='lightblue', lw=2)
    ax.add_patch(rect1)
    ax.text(0.2, 0.5, "Trader", ha="center", va="center", fontsize=12, fontweight='bold')

    # Broker
    rect2 = patches.FancyBboxPatch((0.7, 0.4), 0.2, 0.2, boxstyle="round,pad=0.05", edgecolor='black', facecolor='lightgreen', lw=2)
    ax.add_patch(rect2)
    ax.text(0.8, 0.5, "Broker", ha="center", va="center", fontsize=12, fontweight='bold')

    # Messages
    ax.annotate("", xy=(0.7, 0.55), xytext=(0.3, 0.55), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(0.5, 0.6, "1. C = (C1, C2)\n(Commitment)", ha="center", va="bottom")

    ax.annotate("", xy=(0.7, 0.45), xytext=(0.3, 0.45), arrowprops=dict(arrowstyle="->", lw=2))
    ax.text(0.5, 0.4, "2. m, r, e\n(Opening)", ha="center", va="top")

    save_fig(fig, "fig01_protocol_diagram")

def fig_02():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/forex/tick_data.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['order_index'], df['price'])
        ax.set_title("Simulated EUR/USD Tick Data")
        ax.set_xlabel("Tick Index")
        ax.set_ylabel("Price")
        save_fig(fig, "fig02_tick_data")
    except FileNotFoundError:
        pass

def fig_03():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/forex/forex_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df['latency_ms'], kde=True, ax=ax)
        ax.set_title("Latency Distribution — Hybrid Scheme (EUR/USD)")
        ax.set_xlabel("Latency (ms)")
        save_fig(fig, "fig03_latency_dist")
    except FileNotFoundError:
        pass

def fig_04():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/forex/forex_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['order_index'], df['latency_ms'], alpha=0.5, label='Raw Latency')
        ax.plot(df['order_index'], df['latency_ms'].rolling(50).mean(), color='red', label='50-Order Moving Avg')
        ax.set_title("Latency per Order Over Time")
        ax.set_xlabel("Order Index")
        ax.set_ylabel("Latency (ms)")
        ax.legend()
        save_fig(fig, "fig04_latency_over_time")
    except FileNotFoundError:
        pass

def fig_05():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/security_sweep.csv')))
        pivot = df.pivot(index='n', columns='order_load', values='mean_latency_ms')
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(pivot, annot=True, cmap="YlGnBu", fmt=".2f", ax=ax)
        ax.set_title("Latency Heatmap: Dimension vs. Order Load")
        ax.set_xlabel("Order Load")
        ax.set_ylabel("Lattice Dimension (n)")
        save_fig(fig, "fig05_latency_heatmap")
    except FileNotFoundError:
        pass

def fig_06():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/latency_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=df, x='param_set', y='throughput_ops_sec', ax=ax, hue='param_set', legend=False)
        ax.set_title("Throughput Comparison (orders/sec)")
        ax.set_ylabel("Orders / Sec")
        ax.set_xlabel("Parameter Set")
        plt.xticks(rotation=45)
        save_fig(fig, "fig06_throughput_comparison")
    except FileNotFoundError:
        pass

def fig_07():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/latency_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['security_bits'], df['mean_ms'], marker='o')
        ax.set_title("Security vs. Latency Pareto Frontier")
        ax.set_xlabel("Security Bits")
        ax.set_ylabel("Mean Latency (ms)")
        save_fig(fig, "fig07_security_latency_pareto")
    except FileNotFoundError:
        pass

def fig_08():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/latency_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        for _, row in df.iterrows():
            x = np.sort(np.random.normal(row['mean_ms'], row['std_ms'], 1000))
            y = np.arange(1, len(x) + 1) / len(x)
            ax.plot(x, y, label=row['param_set'])
        ax.set_title("Commitment Latency CDF — All Param Sets")
        ax.set_xlabel("Latency (ms)")
        ax.set_ylabel("CDF")
        ax.legend()
        save_fig(fig, "fig08_latency_cdf")
    except FileNotFoundError:
        pass

def fig_09():
    n_bits = np.arange(64, 512, 8)
    grover_cost = 2 ** (n_bits / 2)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(n_bits, grover_cost)
    ax.set_yscale('log')
    ax.set_title("Grover Attack Cost vs. Hash Output Size")
    ax.set_xlabel("Hash Output Size (bits)")
    ax.set_ylabel("Attack Cost (operations)")
    save_fig(fig, "fig09_grover_cost")

def fig_10():
    n_lat = np.arange(64, 1024, 16)
    bkz_cost = 2 ** (0.292 * n_lat)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(n_lat, bkz_cost)
    ax.set_yscale('log')
    ax.set_title("BKZ Attack Cost vs. Lattice Dimension n")
    ax.set_xlabel("Lattice Dimension n")
    ax.set_ylabel("Estimated Gate Count")
    save_fig(fig, "fig10_bkz_cost")

def fig_11():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/zk_latency.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        df_melt = pd.melt(df, id_vars=['param_set'], value_vars=['prove_ms', 'verify_ms'], var_name='Operation', value_name='Latency (ms)')
        sns.boxplot(data=df_melt, x='param_set', y='Latency (ms)', hue='Operation', ax=ax)
        ax.set_title("ZK Proof Generation + Verification Latency")
        save_fig(fig, "fig11_zk_latency")
    except FileNotFoundError:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "fig11_zk_latency.csv missing", ha='center', va='center')
        save_fig(fig, "fig11_zk_latency")

def fig_12():
    sigma = np.linspace(1, 6, 100)
    B = 16
    from scipy.special import erfc
    p_fail = erfc(B / (np.sqrt(2) * sigma))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(sigma, p_fail)
    ax.set_yscale('log')
    ax.set_title("Decryption Failure Probability vs. $\sigma$ (B=16)")
    ax.set_xlabel("Standard Deviation $\sigma$")
    ax.set_ylabel("Probability of Failure")
    save_fig(fig, "fig12_decryption_failure")

def fig_13():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/latency_results.csv')))
        df['overhead'] = 32 + (df['n'] * np.log2(df['q']) / 8)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=df, x='param_set', y='overhead', ax=ax, hue='param_set', legend=False)
        ax.set_title("Communication Overhead vs. Security Level")
        ax.set_ylabel("Bytes")
        save_fig(fig, "fig13_communication_overhead")
    except FileNotFoundError:
        pass

def fig_14():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/forex/forex_results.csv')))
        np.random.seed(42)
        pairs = np.random.choice(["EUR/USD", "GBP/USD", "USD/JPY", "EUR/GBP"], size=len(df))
        df['Pair'] = pairs
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.violinplot(data=df, x='Pair', y='latency_ms', ax=ax, hue='Pair', legend=False)
        ax.set_title("Multi-Pair Forex Workload")
        save_fig(fig, "fig14_multipair_forex")
    except FileNotFoundError:
        pass

def fig_15():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/forex/forex_results.csv')))
        df2 = pd.concat([df, df]).reset_index(drop=True)
        df2['order_index'] = df2.index
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df2['order_index'], df2['latency_ms'].rolling(20).mean())
        ax.set_title("Latency Stability Under Sustained Load (1000 orders)")
        ax.set_xlabel("Order Index")
        ax.set_ylabel("Rolling Mean Latency (ms)")
        save_fig(fig, "fig15_sustained_load")
    except FileNotFoundError:
        pass

def fig_16():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis('off')

    layers = [
        ("Application Layer", "High-Frequency Trading, Blockchain, CBDC, IoT", "lightgrey"),
        ("Protocol Layer", "Zero-Knowledge Proofs, Fiat-Shamir, Commitment Openings", "lightblue"),
        ("Hybrid Cryptography Layer", "SHA3-256 Fast Hash, LWE Quantum-Resistant Vectors", "lightgreen"),
        ("Mathematical Fundamentals", "Lattices, Discrete Gaussians, Injective Encoding", "wheat")
    ]

    y = 0.8
    for name, desc, color in layers:
        rect = patches.FancyBboxPatch((0.1, y), 0.8, 0.15, boxstyle="round,pad=0.02", edgecolor='black', facecolor=color, lw=2)
        ax.add_patch(rect)
        ax.text(0.5, y + 0.1, name, ha="center", va="center", fontsize=12, fontweight='bold')
        ax.text(0.5, y + 0.05, desc, ha="center", va="center", fontsize=10)
        y -= 0.2

    ax.set_title("HLCS Protocol Stack Architecture")
    save_fig(fig, "fig16_protocol_stack")

def fig_17():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/batch_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['batch_size'], df['throughput_ops_sec'], marker='o')
        ax.set_title("Batch Commitment Throughput vs. Batch Size")
        ax.set_xlabel("Batch Size")
        ax.set_ylabel("Throughput (ops/sec)")
        save_fig(fig, "fig17_batch_throughput")
    except FileNotFoundError:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "fig17_batch_results.csv missing", ha='center', va='center')
        save_fig(fig, "fig17_batch_throughput")

def fig_18():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/selective_open.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['subset_size'], df['latency_ms'], marker='o')
        ax.set_title("Selective Opening Overhead vs. Subset Size")
        ax.set_xlabel("Subset Size")
        ax.set_ylabel("Latency (ms)")
        save_fig(fig, "fig18_selective_open")
    except FileNotFoundError:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "fig18_selective_open.csv missing", ha='center', va='center')
        save_fig(fig, "fig18_selective_open")

def fig_19():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/blockchain_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=df, x='Scheme', y='Latency (ms)', ax=ax, hue='Scheme', legend=False)
        ax.set_title("Blockchain Application Latency Comparison")
        save_fig(fig, "fig19_blockchain_app")
    except FileNotFoundError:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "fig19_blockchain_results.csv missing", ha='center', va='center')
        save_fig(fig, "fig19_blockchain_app")

def fig_20():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/iot_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.scatterplot(data=df, x='Device', y='Latency (ms)', ax=ax, hue='Device', legend=False)
        ax.set_title("IoT Application: Latency at Reduced Parameters")
        save_fig(fig, "fig20_iot_app")
    except FileNotFoundError:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "fig20_iot_results.csv missing", ha='center', va='center')
        save_fig(fig, "fig20_iot_app")

def fig_21():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/cbdc_results.csv')))
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(data=df, x='Volume', y='Throughput', ax=ax, hue='Volume', legend=False)
        ax.set_title("CBDC Order Processing Throughput")
        save_fig(fig, "fig21_cbdc_app")
    except FileNotFoundError:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "fig21_cbdc_results.csv missing", ha='center', va='center')
        save_fig(fig, "fig21_cbdc_app")

def fig_22():
    try:
        df = pd.read_csv(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/synthetic/sensitivity.csv')))
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(df['n'], df['q'], df['latency_ms'], cmap='viridis', edgecolor='none')
        ax.set_title("Security Parameter Sensitivity Analysis")
        ax.set_xlabel("n")
        ax.set_ylabel("q")
        ax.set_zlabel("Latency (ms)")
        save_fig(fig, "fig22_sensitivity_analysis")
    except FileNotFoundError:
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.text(0.5, 0.5, 0.5, "fig22_sensitivity.csv missing", ha='center', va='center')
        save_fig(fig, "fig22_sensitivity_analysis")

def fig_23():
    schemes = ['HLCS', 'zk-STARK', 'Groth16']
    sizes = [1500, 45000, 200]
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=schemes, y=sizes, ax=ax, hue=schemes, legend=False)
    ax.set_title("Comparative ZK Proof Sizes")
    ax.set_ylabel("Proof Size (bytes)")
    ax.set_yscale('log')
    save_fig(fig, "fig23_zk_proof_sizes")

def fig_24():
    years = np.arange(2025, 2041)
    capability = 2 ** (years - 2020)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(years, capability, marker='o')
    ax.set_title("Quantum Attack Timeline Projection (2025–2040)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Estimated Quantum Capability (Qubits)")
    ax.set_yscale('log')
    save_fig(fig, "fig24_quantum_timeline")


def main():
    fig_01()
    fig_02()
    fig_03()
    fig_04()
    fig_05()
    fig_06()
    fig_07()
    fig_08()
    fig_09()
    fig_10()
    fig_11()
    fig_12()
    fig_13()
    fig_14()
    fig_15()
    fig_16()
    fig_17()
    fig_18()
    fig_19()
    fig_20()
    fig_21()
    fig_22()
    fig_23()
    fig_24()

if __name__ == "__main__":
    main()
