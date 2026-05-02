import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set global matplotlib styles
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
                     'xtick.labelsize': 10, 'ytick.labelsize': 10,
                     'figure.dpi': 300, 'savefig.dpi': 300})

def generate_eda_plots():
    data_path = 'heart_mind_cvd/data/nhis_processed.csv'
    output_dir = 'heart_mind_cvd/outputs/figures/'
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(data_path)

    # 1. Target Class Distribution
    plt.figure()
    sns.countplot(x='label', data=df)
    plt.title('Target Class Distribution')
    plt.savefig(os.path.join(output_dir, 'target_distribution.png'), bbox_inches='tight')
    plt.close()

    # 2. Mental Health Co-morbidities vs CVD Risk
    if 'ANXEV_A' in df.columns and 'DEPEV_A' in df.columns:
        # Anxiety vs CVD Risk
        plt.figure()
        sns.countplot(x='ANXEV_A', hue='label', data=df)
        plt.title('Anxiety vs CVD Risk')
        plt.savefig(os.path.join(output_dir, 'anxiety_vs_cvd.png'), bbox_inches='tight')
        plt.close()

        # Depression vs CVD Risk
        plt.figure()
        sns.countplot(x='DEPEV_A', hue='label', data=df)
        plt.title('Depression vs CVD Risk')
        plt.savefig(os.path.join(output_dir, 'depression_vs_cvd.png'), bbox_inches='tight')
        plt.close()

    print("EDA plots generated successfully.")

if __name__ == "__main__":
    generate_eda_plots()
