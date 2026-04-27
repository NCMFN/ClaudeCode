import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import logging
from datetime import datetime
import glob

# Determinism
np.random.seed(42)

# Global plot styling
plt.rcParams.update({
    'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'figure.dpi': 300, 'savefig.dpi': 300
})

os.makedirs("results/logs", exist_ok=True)
os.makedirs("results/figures", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

logging.basicConfig(
    filename="results/logs/preprocessing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def validate_schema(df):
    required_cols = {'DeviceID', 'EnergyConsumption_kWh', 'DeviceStatus', 'SensorReading', 'Timestamp', 'CommandType'}
    if not required_cols.issubset(set(df.columns)):
        missing = required_cols - set(df.columns)
        error_msg = f"Missing required columns: {missing}"
        logging.error(error_msg)
        with open("results/logs/error.log", "w") as f:
            f.write(error_msg + "\nSuggestion: Verify dataset download or generation.\n")
        raise ValueError(error_msg)

def preprocess_data():
    start_time = datetime.now()
    logging.info("Starting preprocessing")

    # Load dataset
    data_files = glob.glob("data/primary/*.csv")
    if not data_files:
        raise FileNotFoundError("No CSV files found in data/primary/")

    df = pd.read_csv(data_files[0])
    validate_schema(df)

    # Data Cleaning
    initial_len = len(df)
    df = df.dropna(subset=['SensorReading', 'EnergyConsumption_kWh'])
    dropped = initial_len - len(df)
    logging.info(f"Dropped {dropped} rows with nulls")

    # Feature Engineering
    Emin = df['EnergyConsumption_kWh'].min()
    Emax = df['EnergyConsumption_kWh'].max()
    df['SoC'] = (df['EnergyConsumption_kWh'] - Emin) / (Emax - Emin) * 100

    df['DeviceStatus'] = df['DeviceStatus'].map({'active': 1, 'idle': 0})

    # Simulate blockchain events
    df['blockchain_event'] = 0
    df.loc[df.index % 60 == 0, 'blockchain_event'] = 1

    # Validations
    assert df['SoC'].between(0, 100).all(), "SoC must be between 0 and 100"
    assert not df.isna().any().any(), "No NaNs should exist"

    # Plot Energy Distribution
    plt.figure()
    plt.hist(df['EnergyConsumption_kWh'], bins=50, color='skyblue', edgecolor='black')
    plt.title('Energy Consumption Distribution')
    plt.xlabel('Energy (kWh)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig('results/figures/energy_distribution.png')
    plt.close()
    logging.info("Saved energy distribution plot")

    # Time-based split
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values('Timestamp')

    split_idx = int(len(df) * 0.7)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    train_df.to_csv("data/processed/train.csv", index=False)
    test_df.to_csv("data/processed/test.csv", index=False)

    end_time = datetime.now()
    logging.info(f"Preprocessing completed in {end_time - start_time}. Train size: {len(train_df)}, Test size: {len(test_df)}")
    print("Preprocessing successful.")

if __name__ == "__main__":
    try:
        preprocess_data()
    except Exception as e:
        logging.error(f"Execution failed: {str(e)}")
        with open("results/logs/error.log", "w") as f:
            f.write(f"Error: {str(e)}\nSuggestion: Check data integrity and schema.\n")
        raise
