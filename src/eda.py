import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Standard rcParams for clear plots
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def run_eda(df: pd.DataFrame, out_dir: str):
    """
    Performs EDA on the dataset and saves plots to out_dir.
    """
    os.makedirs(out_dir, exist_ok=True)

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # 1. Histograms
    print("Generating histograms...")
    for col in numeric_cols:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col], kde=True, color='#1F3864')
        plt.title(f'Histogram of {col}')
        plt.xlabel(col)
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'hist_{col}.png'))
        plt.close()

    # 2. Correlation Heatmap
    print("Generating correlation heatmap...")
    plt.figure(figsize=(12, 10))
    corr = df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, annot_kws={'size': 7}, cmap='coolwarm', fmt=".2f")
    plt.title('Feature Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'correlation_heatmap.png'))
    plt.close()

    # 3. 3D Scatter Plot
    print("Generating 3D scatter plot...")
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(df['Noise_Level'], df['Residual_Energy'], df['Detection_Accuracy'],
                    c=df['Detection_Accuracy'], cmap='viridis', alpha=0.6)
    ax.set_xlabel('Ambient Noise (dB)')
    ax.set_ylabel('Residual Energy (%)')
    ax.set_zlabel('Detection Accuracy (%)')
    plt.colorbar(sc, label='Detection Accuracy (%)')
    plt.title('Noise vs Energy vs Detection Accuracy')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, '3d_scatter.png'))
    plt.close()

    # 4. Accuracy decay non-linearly below 15% residual energy in high-noise
    print("Generating accuracy decay analysis...")
    high_noise_thresh = df['Noise_Level'].quantile(0.75)
    high_noise_df = df[df['Noise_Level'] >= high_noise_thresh]

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=high_noise_df, x='Residual_Energy', y='Detection_Accuracy', alpha=0.5)
    sns.regplot(data=high_noise_df, x='Residual_Energy', y='Detection_Accuracy', scatter=False, lowess=True, color='red')
    plt.axvline(x=15, color='orange', linestyle='--', label='15% Energy Threshold')
    plt.title('Detection Accuracy vs Residual Energy (High Noise Environments)')
    plt.xlabel('Residual Energy (%)')
    plt.ylabel('Detection Accuracy (%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'accuracy_decay_high_noise.png'))
    plt.close()

    # 5. Pairplots for key features
    print("Generating pairplot...")
    key_features = ['Residual_Energy', 'Noise_Level', 'Signal_Strength', 'SNR', 'Transmission_Power', 'Detection_Accuracy']
    # Sample down to 1000 for pairplot speed
    sample_df = df[key_features].sample(n=min(1000, len(df)), random_state=42)
    g = sns.pairplot(sample_df, plot_kws={'alpha': 0.5})
    g.fig.suptitle('Pairplot of Key Features', y=1.02)
    plt.savefig(os.path.join(out_dir, 'pairplot.png'))
    plt.close()

if __name__ == "__main__":
    from data_loader import download_data, load_all_datasets
    p_path, _, _ = download_data()
    df = load_all_datasets(p_path, None, None)
    run_eda(df, "results/figures")
