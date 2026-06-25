import pandas as pd
import numpy as np
from datetime import datetime

def load_and_clean_data(raw_file_path):
    # Load dataset
    # The file has semicolon delimiters
    df = pd.read_csv(raw_file_path, sep=';')

    # Drop rows with null Price or missing Departure/Arrival Station
    df.dropna(subset=['Price', 'Departure Station', 'Arrival Destination'], inplace=True)
    df = df[df['Price'].notna()]
    # Remove rows where price is 0 if any
    # (The prompt doesn't explicitly mention it, but it's good practice. We'll leave it out to stick to prompt strictly)

    # Parse `Date of Purchase` and `Time of Purchase` into a single `transaction_datetime` column
    df['transaction_datetime'] = pd.to_datetime(df['Date of Purchase'] + ' ' + df['Time of Purchase'], format="%d/%m/%Y %H:%M:%S")

    # Parse `Date of Journey` and `Departure Time` into `journey_datetime`
    df['journey_datetime'] = pd.to_datetime(df['Date of Journey'] + ' ' + df['Departure Time'], format="%d/%m/%Y %H:%M:%S")

    # Compute `advance_booking_days` = (`journey_datetime` - `transaction_datetime`).days
    df['advance_booking_days'] = (df['journey_datetime'] - df['transaction_datetime']).dt.days

    # Extract `hour_of_purchase`, `day_of_week`, `month`, `is_weekend` from `transaction_datetime`
    df['hour_of_purchase'] = df['transaction_datetime'].dt.hour
    df['day_of_week'] = df['transaction_datetime'].dt.dayofweek
    df['month'] = df['transaction_datetime'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    # Extract `hour_of_departure` from `journey_datetime`
    df['hour_of_departure'] = df['journey_datetime'].dt.hour

    # Compute `scheduled_journey_duration_mins` from `Departure Time` to `Arrival Time`
    # Arrival Time may be on the next day if Arrival Time < Departure Time
    dep_time = pd.to_timedelta(df['Departure Time'])
    arr_time = pd.to_timedelta(df['Arrival Time'])
    duration = arr_time - dep_time
    # handle next-day arrivals
    duration = duration.apply(lambda x: x + pd.Timedelta(days=1) if x.days < 0 else x)
    df['scheduled_journey_duration_mins'] = duration.dt.total_seconds() / 60

    # Compute `actual_delay_mins` = `Actual Arrival Time` - `Arrival Time` (handle next-day arrivals)
    actual_arr_time = pd.to_timedelta(df['Actual Arrival Time'])
    delay = actual_arr_time - arr_time

    # We might have next day issue again, or next day if delayed.
    # E.g. scheduled arrival 23:50, actual 00:10 -> delay is 20 mins.
    # actual_arr_time (00:10) - arr_time (23:50) = -23:40
    # Add 1 day if delay < -12 hours (to be safe)
    delay = delay.apply(lambda x: x + pd.Timedelta(days=1) if x.total_seconds() < -12*3600 else x)
    df['actual_delay_mins'] = delay.dt.total_seconds() / 60
    # Clean up NaNs in delay if any
    df['actual_delay_mins'] = df['actual_delay_mins'].fillna(0)

    # Flag `is_delayed` = 1 if `actual_delay_mins` > 5
    df['is_delayed'] = (df['actual_delay_mins'] > 5).astype(int)

    return df

if __name__ == "__main__":
    df = load_and_clean_data("uk-rail-pricing/data/raw/railway.csv")
    print(df.head())
    print(df.shape)
