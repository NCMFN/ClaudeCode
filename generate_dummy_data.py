import pandas as pd
import numpy as np

# Columns required: DeviceID, EnergyConsumption_kWh, DeviceStatus, SensorReading, Timestamp, CommandType.

np.random.seed(42)
n_rows = 1000

dates = pd.date_range(start='2023-01-01', periods=n_rows, freq='1min')
data = {
    'DeviceID': np.random.choice(['Dev_1', 'Dev_2', 'Dev_3', 'Dev_4'], size=n_rows),
    'EnergyConsumption_kWh': np.random.uniform(0.1, 5.0, size=n_rows),
    'DeviceStatus': np.random.choice(['active', 'idle'], size=n_rows),
    'SensorReading': np.random.uniform(20.0, 30.0, size=n_rows),
    'Timestamp': dates,
    'CommandType': np.random.choice(['cmd_a', 'cmd_b', 'cmd_c'], size=n_rows)
}

# introduce some nulls to test missing values dropping
data['SensorReading'][10] = np.nan
data['EnergyConsumption_kWh'][20] = np.nan

df = pd.DataFrame(data)
df.to_csv('data/primary/iot_dataset.csv', index=False)
print(df.head())
