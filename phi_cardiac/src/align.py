import pandas as pd
import numpy as np
import os

def align_data(cities, raw_dir, processed_dir):
    os.makedirs(processed_dir, exist_ok=True)
    all_city_data = []

    for city in cities:
        city_slug = city.lower().replace(" ", "_")

        # Load datasets
        aq_file = os.path.join(raw_dir, f'openaq_{city_slug}.csv')
        era5_file = os.path.join(raw_dir, f'era5_{city_slug}.csv')
        health_file = os.path.join(raw_dir, f'health_{city_slug}.csv')

        if not (os.path.exists(aq_file) and os.path.exists(era5_file) and os.path.exists(health_file)):
            print(f"Missing data for {city}. Skipping.")
            continue

        aq_df = pd.read_csv(aq_file, parse_dates=['date'])
        era5_df = pd.read_csv(era5_file, parse_dates=['date'])
        health_df = pd.read_csv(health_file, parse_dates=['date'])

        # Left join air quality + meteorology
        merged = pd.merge(aq_df, era5_df, on=['date', 'city'], how='left')

        # Join with cardiac events
        merged = pd.merge(merged, health_df, on=['date', 'city'], how='left')

        # Sort by date
        merged = merged.sort_values('date')

        # Handle missing days: interpolate air quality gaps <= 3 days
        cols_to_interpolate = ['pm25_mean', 'no2_mean', 'o3_mean']

        # Create an is_imputed flag before interpolating
        merged['is_imputed'] = merged[cols_to_interpolate].isnull().any(axis=1).astype(int)

        for col in cols_to_interpolate:
            # Linear interpolation with limit=3
            interpolated = merged[col].interpolate(method='linear', limit=3)
            merged[col] = interpolated

        # If there are still NaNs after limit=3 interpolation, we mark is_imputed and could drop or fill
        # We will forward fill then backward fill just to have complete data for lag features
        merged[cols_to_interpolate] = merged[cols_to_interpolate].ffill().bfill()

        # 24h, 48h, 72h lagged variables for PM2.5 and temperature
        merged['pm25_lag24'] = merged['pm25_mean'].shift(1)
        merged['pm25_lag48'] = merged['pm25_mean'].shift(2)
        merged['pm25_lag72'] = merged['pm25_mean'].shift(3)

        merged['t2m_lag24'] = merged['t2m'].shift(1)
        merged['t2m_lag48'] = merged['t2m'].shift(2)
        merged['t2m_lag72'] = merged['t2m'].shift(3)

        # Compute seasonal Z-scores for temperature normalization
        # subtract rolling 30-day mean, divide by rolling 30-day std
        merged['t2m_roll_mean_30d'] = merged['t2m'].rolling(window=30, min_periods=1).mean()
        merged['t2m_roll_std_30d'] = merged['t2m'].rolling(window=30, min_periods=1).std()

        # Avoid division by zero
        std_safe = merged['t2m_roll_std_30d'].replace(0, 1)
        std_safe = std_safe.fillna(1)

        merged['t2m_zscore'] = (merged['t2m'] - merged['t2m_roll_mean_30d']) / std_safe

        # Forward fill lags to avoid NaNs at start
        merged = merged.bfill()

        all_city_data.append(merged)

    if all_city_data:
        final_panel = pd.concat(all_city_data, ignore_index=True)
        output_file = os.path.join(processed_dir, 'phi_panel.csv')
        final_panel.to_csv(output_file, index=False)
        print(f"Saved merged panel to {output_file}")
    else:
        print("No data processed.")

if __name__ == "__main__":
    target_cities = ["New York", "Los Angeles", "London", "Mumbai", "Lagos"]
    align_data(
        cities=target_cities,
        raw_dir="data/raw",
        processed_dir="data/processed"
    )
