import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

def main():
    files = glob.glob('data/primary/*.csv')
    if not files:
        print("No CSV files found in data/primary/")
        return

    df_list = [pd.read_csv(f) for f in files]
    df = pd.concat(df_list, ignore_index=True)

    # 1. Verify required columns
    required_cols = ['DeviceID', 'EnergyConsumption_kWh', 'DeviceStatus', 'SensorReading', 'Timestamp', 'CommandType']
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

    # 5. Handle missing values: drop rows with null SensorReading or EnergyConsumption
    initial_len = len(df)
    df = df.dropna(subset=['SensorReading', 'EnergyConsumption_kWh'])
    print(f"Dropped {initial_len - len(df)} rows due to missing values.")

    # 2. Map EnergyConsumption_kWh to synthetic SoC percentage
    e_min = df['EnergyConsumption_kWh'].min()
    e_max = df['EnergyConsumption_kWh'].max()
    df['SoC'] = (df['EnergyConsumption_kWh'] - e_min) / (e_max - e_min) * 100

    assert df['SoC'].min() >= 0 and df['SoC'].max() <= 100, "SoC normalisation failed."

    # 3. Encode DeviceStatus as binary: active=1, idle=0
    df['DeviceStatus'] = df['DeviceStatus'].apply(lambda x: 1 if x == 'active' else 0)

    # 4. Create blockchain_event column: value=1 every 60 rows
    df = df.sort_values('Timestamp').reset_index(drop=True)
    df['blockchain_event'] = 0
    df.loc[df.index % 60 == 0, 'blockchain_event'] = 1

    # 6. Time-based split: 70% train, 30% test
    split_idx = int(len(df) * 0.7)
    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    # Validation checks
    assert train_df.isnull().sum().sum() == 0, "Nulls found in train"
    assert test_df.isnull().sum().sum() == 0, "Nulls found in test"

    print("Class balance DeviceStatus Train:")
    print(train_df['DeviceStatus'].value_counts(normalize=True))
    print("Class balance DeviceStatus Test:")
    print(test_df['DeviceStatus'].value_counts(normalize=True))

    # Save
    train_df.to_csv('data/processed/train.csv', index=False)
    test_df.to_csv('data/processed/test.csv', index=False)

    # Plot energy consumption distribution
    plt.figure(figsize=(10, 6))
    plt.hist(df['EnergyConsumption_kWh'], bins=50, alpha=0.7, color='blue', edgecolor='black')
    plt.title('Energy Consumption Distribution (kWh)')
    plt.xlabel('Energy Consumption (kWh)')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.savefig('results/figures/energy_distribution.png')
    plt.close()

if __name__ == "__main__":
    main()
