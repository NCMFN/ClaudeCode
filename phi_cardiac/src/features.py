import pandas as pd
import numpy as np
import os

def create_features(input_file, output_file):
    df = pd.read_csv(input_file, parse_dates=['date'])

    # Construct the Pollution-Heat Index:
    # PHI = alpha * T_standardized + beta * PM25_concentration + gamma * (T_standardized * PM25_concentration)
    alpha, beta, gamma = 1.0, 1.0, 1.0

    df['phi_initial'] = alpha * df['t2m_zscore'] + beta * df['pm25_mean'] + gamma * (df['t2m_zscore'] * df['pm25_mean'])

    # Add features: day_of_week, month, is_weekend
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    # is_heatwave (flag if T > 95th percentile for that city-month)
    df['is_heatwave'] = 0
    for city in df['city'].unique():
        for month in df['month'].unique():
            mask = (df['city'] == city) & (df['month'] == month)
            p95 = df[mask]['t2m'].quantile(0.95)
            df.loc[mask & (df['t2m'] > p95), 'is_heatwave'] = 1

    # pm25_3day_rolling_mean, temp_3day_rolling_mean
    # Need to compute grouped by city to avoid rolling across cities
    df = df.sort_values(['city', 'date'])

    df['pm25_3day_rolling_mean'] = df.groupby('city')['pm25_mean'].transform(lambda x: x.rolling(window=3, min_periods=1).mean())
    df['temp_3day_rolling_mean'] = df.groupby('city')['t2m'].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

    # Target variable: log1p transform daily_cardiac_admissions for normality
    df['target_log1p'] = np.log1p(df['daily_cardiac_admissions'])

    # Split mapping using a column (to make it easy for training)
    # train on 2015-2020, validate 2021, test 2022-2023
    df['split'] = 'train'
    df.loc[df['date'].dt.year == 2021, 'split'] = 'val'
    df.loc[df['date'].dt.year >= 2022, 'split'] = 'test'

    df.to_csv(output_file, index=False)
    print(f"Features created and saved to {output_file}")

if __name__ == "__main__":
    create_features(
        input_file="data/processed/phi_panel.csv",
        output_file="data/processed/phi_features.csv"
    )
