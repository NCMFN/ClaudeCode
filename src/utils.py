import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_degradation_trends(df, output_dir='.'):
    if df.empty:
        return

    os.makedirs(output_dir, exist_ok=True)

    plt.rcParams.update({
        'font.size': 11,
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'figure.dpi': 300,
        'savefig.dpi': 300
    })

    # 1. Plot RUL vs. Thermal_Log for each failure class
    if 'RUL' in df.columns and 'Thermal_Log' in df.columns and 'Failure_Label' in df.columns:
        plt.figure(figsize=(10, 6))
        for label in df['Failure_Label'].unique():
            subset = df[df['Failure_Label'] == label]
            # Plot a smooth trend line
            try:
                z = np.polyfit(subset['Thermal_Log'], subset['RUL'], 2)
                p = np.poly1d(z)
                x = np.linspace(subset['Thermal_Log'].min(), subset['Thermal_Log'].max(), 100)
                plt.plot(x, p(x), label=f'Class {label}')
            except:
                plt.scatter(subset['Thermal_Log'], subset['RUL'], alpha=0.3, label=f'Class {label}')

        plt.title('Degradation Model: RUL vs Thermal Log')
        plt.xlabel('Thermal Log (°C)')
        plt.ylabel('Remaining Useful Life (RUL)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'rul_vs_thermal.png'), dpi=300)
        plt.close()

    # 2. Exponential failure risk curve above 85C
    plt.figure(figsize=(8, 6))
    temps = np.linspace(40, 100, 100)
    risk = np.where(temps > 85, np.exp(0.5 * (temps - 85)), 1.0)
    plt.plot(temps, risk, 'r-', linewidth=2)
    plt.axvline(x=85, color='k', linestyle='--', label='Critical Threshold (85°C)')
    plt.title('Exponential Failure Risk Profile')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Relative Failure Risk')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'exponential_risk.png'), dpi=300)
    plt.close()

    # 3. Failure probability vs. cumulative Peak_Excursion count
    if 'Peak_Excursion' in df.columns and 'Failure_Label' in df.columns:
        plt.figure(figsize=(8, 6))
        # Simplify probability as ratio of failures
        # Convert multiclass to binary failure for this plot
        df['Is_Failure'] = (df['Failure_Label'] != 0).astype(int)
        try:
            prob = df.groupby(pd.qcut(df['Peak_Excursion'], q=10, duplicates='drop'))['Is_Failure'].mean()
            prob.plot(kind='line', marker='o')
        except:
            # Fallback if qcut fails
            prob = df.groupby('Peak_Excursion')['Is_Failure'].mean().head(20)
            prob.plot(kind='bar')

        plt.title('Failure Probability vs Peak Excursion Count')
        plt.xlabel('Cumulative Peak Excursions (>85°C)')
        plt.ylabel('Failure Probability')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'failure_prob_vs_excursion.png'), dpi=300)
        plt.close()

if __name__ == "__main__":
    try:
        df = pd.read_parquet('data/processed/train_features.parquet')
        plot_degradation_trends(df)
    except:
        pass
