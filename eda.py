import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import kagglehub

def load_data(data_path=None):
    """Loads the loan default dataset."""
    if data_path is None or not os.path.exists(data_path):
        print("Data path not provided or not found. Downloading via kagglehub...")
        base_path = kagglehub.dataset_download('nikhil1e9/loan-default')
        data_path = os.path.join(base_path, 'Loan_default.csv')
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Could not find Loan_default.csv in {base_path}")

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    return df

def perform_eda(df, output_dir='outputs'):
    """Performs EDA and generates required plots."""
    os.makedirs(output_dir, exist_ok=True)

    print("--- Dataset Statistics ---")
    print(f"Shape: {df.shape}")
    print("\nData Types:")
    print(df.dtypes)

    null_counts = df.isnull().sum()
    print("\nNull Counts:")
    print(null_counts[null_counts > 0])

    # Flag > 30% missing
    high_missing = null_counts[null_counts > 0.3 * len(df)]
    if not high_missing.empty:
        print("\nColumns with >30% missing values:")
        for col, count in high_missing.items():
            print(f"- {col}: {count} ({count/len(df)*100:.2f}%)")
    else:
        print("\nNo columns with >30% missing values.")

    class_balance = df['Default'].value_counts(normalize=True)
    print("\nClass Balance (Default):")
    print(class_balance * 100)

    print("\nGenerating plots...")

    # 1. Interest Rate vs Default (boxplot)
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='Default', y='InterestRate', data=df)
    plt.title('Interest Rate vs Default')
    plt.xlabel('Default (0 = Safe, 1 = Default)')
    plt.ylabel('Interest Rate (%)')
    plt.savefig(os.path.join(output_dir, 'interest_rate_vs_default.png'))
    plt.close()

    # 2. DTI vs Default (boxplot)
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='Default', y='DTIRatio', data=df)
    plt.title('DTI Ratio vs Default')
    plt.xlabel('Default (0 = Safe, 1 = Default)')
    plt.ylabel('DTI Ratio')
    plt.savefig(os.path.join(output_dir, 'dti_vs_default.png'))
    plt.close()

    # 3. Credit Score histogram by class
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='CreditScore', hue='Default', bins=50, kde=True, palette='viridis')
    plt.title('Credit Score Distribution by Class')
    plt.xlabel('Credit Score')
    plt.ylabel('Count')
    plt.savefig(os.path.join(output_dir, 'credit_score_hist.png'))
    plt.close()

    # 4. Correlation Matrix Heatmap
    numeric_df = df.select_dtypes(include=['int64', 'float64']).drop(columns=['LoanID'], errors='ignore')
    corr_matrix = numeric_df.corr()

    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
    plt.title('Correlation Matrix of Numeric Features')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_matrix.png'))
    plt.close()

    print(f"EDA plots saved to {output_dir}/")

if __name__ == "__main__":
    df = load_data()
    perform_eda(df)
