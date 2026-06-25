import pandas as pd
import numpy as np
from rapidfuzz import process, fuzz
from haversine import haversine, Unit
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os
from sklearn.preprocessing import StandardScaler

import data_loader

def engineer_features(df, stations_df):
    os.makedirs('uk-rail-pricing/outputs/figures', exist_ok=True)
    os.makedirs('uk-rail-pricing/data/processed', exist_ok=True)

    # Global settings for matplotlib
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

    # Target Variable: price_gbp
    df['price_gbp'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['price_gbp'])

    # Peak Flag: is_peak = 1 if hour_of_departure is between 6–8 or 16–18 on a weekday
    df['is_peak'] = ((df['hour_of_departure'].isin([6, 7, 8, 16, 17, 18])) & (df['day_of_week'] < 5)).astype(int)

    # Railcard Binary Flags: has_railcard, is_senior, is_disabled
    df['has_railcard'] = (df['Railcard'] != 'None').astype(int)
    df['is_senior'] = (df['Railcard'] == 'Senior').astype(int)
    df['is_disabled'] = (df['Railcard'] == 'Disabled').astype(int)

    # One-Hot Encoding: Ticket Class, Ticket Type, Railcard, Reason for Delay
    df = pd.get_dummies(df, columns=['Ticket Class', 'Ticket Type', 'Railcard', 'Reason for Delay'], drop_first=False)
    # clean column names
    df.columns = [str(c).replace(' ', '_') for c in df.columns]

    # Node Mapping
    station_names = stations_df['stationName'].unique()

    # Create a mapping dictionary to save fuzzy match results
    match_cache = {}
    def get_best_match(name):
        if pd.isna(name): return None
        if name in match_cache: return match_cache[name]
        # Exact match first
        if name in station_names:
            match_cache[name] = name
            return name
        # Fuzzy match
        match = process.extractOne(name, station_names, scorer=fuzz.WRatio, score_cutoff=85)
        if match:
            match_cache[name] = match[0]
            return match[0]
        else:
            match_cache[name] = None
            return None

    df['dep_match'] = df['Departure_Station'].apply(get_best_match)
    df['arr_match'] = df['Arrival_Destination'].apply(get_best_match)

    unmatched = set(df[df['dep_match'].isna()]['Departure_Station'].unique()) | set(df[df['arr_match'].isna()]['Arrival_Destination'].unique())
    with open('uk-rail-pricing/data/processed/unmatched_stations.txt', 'w') as f:
        for u in unmatched:
            f.write(f"{u}\n")

    # Merge departure
    stations_sub = stations_df[['stationName', 'lat', 'long']].rename(columns={'stationName': 'dep_match', 'lat': 'departure_lat', 'long': 'departure_lon'})
    df = df.merge(stations_sub, on='dep_match', how='left')

    # Merge arrival
    stations_sub = stations_df[['stationName', 'lat', 'long']].rename(columns={'stationName': 'arr_match', 'lat': 'arrival_lat', 'long': 'arrival_lon'})
    df = df.merge(stations_sub, on='arr_match', how='left')

    # Drop rows without coords
    df = df.dropna(subset=['departure_lat', 'departure_lon', 'arrival_lat', 'arrival_lon'])

    # Distance Feature: Compute haversine_distance_km
    def calc_dist(row):
        return haversine((row['departure_lat'], row['departure_lon']), (row['arrival_lat'], row['arrival_lon']), unit=Unit.KILOMETERS)

    df['haversine_distance_km'] = df.apply(calc_dist, axis=1)

    # Apply StandardScaler to continuous features
    scaler = StandardScaler()
    continuous_features = ['advance_booking_days', 'haversine_distance_km', 'scheduled_journey_duration_mins', 'hour_of_departure', 'hour_of_purchase']
    df[continuous_features] = scaler.fit_transform(df[continuous_features])

    import pickle
    with open('uk-rail-pricing/outputs/models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)

    df.to_csv('uk-rail-pricing/data/processed/features_full.csv', index=False)

    # Output Figure 1: Correlation heatmap of all numeric features vs. price_gbp
    plt.figure(figsize=(12, 10))
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    # Ensure boolean/dummy columns are numeric
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    corr = df[numeric_cols].corr()
    plt_sns.heatmap(corr[['price_gbp']].sort_values(by='price_gbp', ascending=False), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Figure 1: Feature Correlation with Price")
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_1.png')
    plt.close()

    # Need original data for Figure 2 and 3 so we don't use scaled/dummy data
    # Figure 2: Distribution of price_gbp by Ticket Type and Ticket Class (violin plot)
    # Reconstruct original ticket types/classes for plotting or use original dataframe
    # The prompt states: Distribution of `price_gbp` by Ticket Type and Ticket Class (violin plot)
    # We will use original dataframe to get the labels before dummy encoding
    pass

def generate_figs(original_df):
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
    original_df['price_gbp'] = pd.to_numeric(original_df['Price'], errors='coerce')

    # Figure 2: Distribution of price_gbp by Ticket Type and Ticket Class (violin plot)
    plt.figure(figsize=(10, 6))
    plt_sns.violinplot(data=original_df, x='Ticket Type', y='price_gbp', hue='Ticket Class', split=True)
    plt.title('Figure 2: Price Distribution by Ticket Type and Class\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_2.png')
    plt.close()

    # Figure 3: Advance booking days vs. price scatter with regression line by ticket type
    plt.figure(figsize=(10, 6))
    plt_sns.lmplot(data=original_df, x='advance_booking_days', y='price_gbp', hue='Ticket Type', scatter_kws={'alpha': 0.5})
    plt.title('Figure 3: Advance Booking Days vs Price\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_3.png')
    plt.close()

if __name__ == "__main__":
    df = data_loader.load_and_clean_data("uk-rail-pricing/data/raw/railway.csv")
    stations_df = pd.read_csv("uk-rail-pricing/data/geospatial/stations.csv")
    generate_figs(df.copy())
    engineer_features(df, stations_df)
    print("Feature engineering complete.")
