import pandas as pd
import numpy as np
import datetime
import os

def load_and_clean_data(raw_data_path, stations_path):
    print("Loading data...")
    # Read with auto-detect separator
    df = pd.read_csv(raw_data_path, sep=None, engine='python', on_bad_lines='skip')

    # Drop rows with null Price or missing Departure/Arrival Station
    df = df.dropna(subset=['Price', 'Departure Station', 'Arrival Destination'])

    # Parse dates without strict format to handle both DD/MM/YYYY and YYYY-MM-DD
    df['transaction_datetime'] = pd.to_datetime(df['Date of Purchase'] + ' ' + df['Time of Purchase'], errors='coerce')
    df['journey_datetime'] = pd.to_datetime(df['Date of Journey'] + ' ' + df['Departure Time'], errors='coerce')
    df['Arrival Time DT'] = pd.to_datetime(df['Date of Journey'] + ' ' + df['Arrival Time'], errors='coerce')

    next_day_mask = df['Arrival Time DT'] < df['journey_datetime']
    df.loc[next_day_mask, 'Arrival Time DT'] += pd.Timedelta(days=1)

    df['Actual Arrival DT'] = pd.to_datetime(df['Date of Journey'] + ' ' + df['Actual Arrival Time'], errors='coerce')
    next_day_mask_actual = df['Actual Arrival DT'] < df['journey_datetime']
    df.loc[next_day_mask_actual, 'Actual Arrival DT'] += pd.Timedelta(days=1)

    df['advance_booking_days'] = (df['journey_datetime'] - df['transaction_datetime']).dt.days
    df['hour_of_purchase'] = df['transaction_datetime'].dt.hour
    df['day_of_week'] = df['transaction_datetime'].dt.dayofweek
    df['month'] = df['transaction_datetime'].dt.month
    df['is_weekend'] = df['transaction_datetime'].dt.dayofweek >= 5
    df['hour_of_departure'] = df['journey_datetime'].dt.hour

    df['scheduled_journey_duration_mins'] = (df['Arrival Time DT'] - df['journey_datetime']).dt.total_seconds() / 60

    df['actual_delay_mins'] = (df['Actual Arrival DT'] - df['Arrival Time DT']).dt.total_seconds() / 60
    df['actual_delay_mins'] = df['actual_delay_mins'].apply(lambda x: x if pd.isna(x) or x > -720 else x + 1440)

    df['is_delayed'] = (df['actual_delay_mins'] > 5).astype(int)

    return df
