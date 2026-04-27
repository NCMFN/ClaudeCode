import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import os

os.makedirs("data/primary", exist_ok=True)
os.makedirs("results/logs", exist_ok=True)
logging.basicConfig(
    filename="results/logs/download.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generate_data():
    logging.info("Generating dataset...")
    print("Generating dataset...")

    np.random.seed(42)
    n_rows = 10000

    start_time = datetime(2023, 1, 1)
    timestamps = [start_time + timedelta(minutes=i) for i in range(n_rows)]

    device_ids = ['DEV_001', 'DEV_002', 'DEV_003', 'DEV_004', 'DEV_005']

    df = pd.DataFrame({
        'DeviceID': np.random.choice(device_ids, n_rows),
        'EnergyConsumption_kWh': np.random.uniform(0.1, 5.0, n_rows),
        'DeviceStatus': np.random.choice(['active', 'idle'], n_rows, p=[0.7, 0.3]),
        'SensorReading': np.random.normal(25, 5, n_rows),
        'Timestamp': timestamps,
        'CommandType': np.random.choice(['READ', 'WRITE', 'CONFIG'], n_rows)
    })

    # Introduce some nulls for cleaning step
    null_idx_sensor = np.random.choice(n_rows, 100, replace=False)
    null_idx_energy = np.random.choice(n_rows, 50, replace=False)

    df.loc[null_idx_sensor, 'SensorReading'] = np.nan
    df.loc[null_idx_energy, 'EnergyConsumption_kWh'] = np.nan

    df.to_csv("data/primary/iot_dataset.csv", index=False)
    logging.info("Data generation complete. Saved to data/primary/iot_dataset.csv")
    print("Data generation complete.")

if __name__ == "__main__":
    generate_data()
