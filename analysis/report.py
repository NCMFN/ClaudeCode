import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_report(output_dir: str):
    # Process for both configs
    for t2_key in ['ionq_aria', 'aqt_ring']:
        csv_path = os.path.join(output_dir, f'simulation_results_{t2_key}.csv')
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            continue

        df = pd.read_csv(csv_path)

        # 1. Plot Fidelity decay curve over time (rtt)
        plt.figure(figsize=(10, 6))
        # Sort by RTT to get a smooth curve
        df_sorted = df.sort_values(by='rtt')
        plt.plot(df_sorted['rtt'], df_sorted['true_fidelity'], 'b-', label='True Fidelity')
        plt.axhline(y=0.85, color='r', linestyle='--', label='Security Threshold (0.85)')
        plt.title(f'Fidelity vs RTT ({t2_key})')
        plt.xlabel('RTT (seconds)')
        plt.ylabel('Fidelity')
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, f'fidelity_vs_rtt_{t2_key}.png'))
        plt.close()

        # 2. Compare policies
        # Count total Zombie and Unnecessary Flushes
        zombie_adaptive = df['zombie_adaptive'].sum()
        unnecessary_adaptive = df['unnecessary_flush_adaptive'].sum()

        zombie_static = df['zombie_static'].sum()
        unnecessary_static = df['unnecessary_flush_static'].sum()

        # Bar chart comparison
        labels = ['Zombie Keys Exposed', 'Unnecessary Flushes']
        adaptive_stats = [zombie_adaptive, unnecessary_adaptive]
        static_stats = [zombie_static, unnecessary_static]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 6))
        rects1 = ax.bar(x - width/2, adaptive_stats, width, label='Adaptive TTL')
        rects2 = ax.bar(x + width/2, static_stats, width, label='Static TTL')

        ax.set_ylabel('Count (Simulated Timesteps)')
        ax.set_title(f'Policy Performance Comparison ({t2_key})')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()

        # Add labels on top of bars
        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)

        fig.tight_layout()
        plt.savefig(os.path.join(output_dir, f'policy_comparison_{t2_key}.png'))
        plt.close()

        print(f"Generated plots for {t2_key} in {output_dir}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(__file__))
    output_path = os.path.join(base_dir, 'outputs')
    generate_report(output_path)
