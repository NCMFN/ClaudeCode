import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from rapidfuzz import process, fuzz
import os
from data_loader import load_and_clean_data
from haversine import haversine, Unit

# Shared styling
STYLE = {
    'primary': '#2E5EAA',
    'secondary': '#D9534F'
}

def create_features():
    os.makedirs('outputs/figures', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)

    df = load_and_clean_data('data/raw/railway.csv', 'data/raw/stations.csv')

    # Missing data heatmap (Figure 4) - do this before more cleaning
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
    plt.title('Figure 4: Missing-data heatmap, pre-cleaning. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_04.png', dpi=300)
    plt.close()

    # Rename Price column for convenience
    df['price_gbp'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['price_gbp'])

    # Figure 5: Histogram of raw price_gbp before scaling
    plt.figure(figsize=(10, 6))
    sns.histplot(df['price_gbp'], bins=50, color=STYLE['primary'])
    plt.axvline(df['price_gbp'].mean(), color='red', linestyle='--', label=f"Mean: {df['price_gbp'].mean():.2f}")
    plt.axvline(df['price_gbp'].median(), color='green', linestyle='-', label=f"Median: {df['price_gbp'].median():.2f}")
    plt.legend()
    plt.title('Figure 5: Raw price_gbp histogram. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_05.png', dpi=300)
    plt.close()

    # Figure 2: Distribution of price_gbp by Ticket Type and Ticket Class
    plt.figure(figsize=(12, 6))
    sns.violinplot(data=df, x='Ticket Type', y='price_gbp', hue='Ticket Class', split=True, inner='quartile')
    plt.title('Figure 2: price_gbp distribution by Ticket Type/Class (violin). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_02.png', dpi=300)
    plt.close()

    # Figure 3: Advance booking days vs price scatter with regression line by ticket type
    plt.figure(figsize=(10, 6))
    sns.lmplot(data=df.sample(min(10000, len(df))), x='advance_booking_days', y='price_gbp', hue='Ticket Type', scatter_kws={'alpha': 0.3})
    plt.title('Figure 3: Advance booking days vs price, regression by ticket type. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_03.png', dpi=300)
    plt.close()

    # One-Hot Encoding: Ticket Class, Ticket Type, Railcard, Reason for Delay
    df['Ticket Class'] = df['Ticket Class'].fillna('Unknown')
    df['Ticket Type'] = df['Ticket Type'].fillna('Unknown')
    df['Railcard'] = df['Railcard'].fillna('None')
    df['Reason for Delay'] = df['Reason for Delay'].fillna('NA')

    df_encoded = pd.get_dummies(df, columns=['Ticket Class', 'Ticket Type', 'Railcard', 'Reason for Delay'], drop_first=False)

    # Railcard Binary Flags
    df_encoded['has_railcard'] = (df['Railcard'] != 'None').astype(int)
    df_encoded['is_senior'] = (df['Railcard'] == 'Senior').astype(int)
    df_encoded['is_disabled'] = (df['Railcard'] == 'Disabled').astype(int)

    # Peak Flag: is_peak = 1 if hour_of_departure is between 6-8 or 16-18 on a weekday
    df_encoded['is_peak'] = ((df_encoded['hour_of_departure'].between(6, 8) | df_encoded['hour_of_departure'].between(16, 18)) & ~df_encoded['is_weekend']).astype(int)

    # Node Mapping
    stations = pd.read_csv('data/raw/stations.csv')
    # Use fallback schema if necessary, though our read of stations.csv shows:
    # stationName,lat,long,crsCode,iataAirportCode,constituentCountry
    # The review said prompt provided 'name', 'latitude', 'longitude', 'crs'.
    # But the raw dataset downloaded has 'stationName', 'lat', 'long'.
    # We will rename to standardise internally based on what was read
    if 'stationName' in stations.columns:
        stations = stations.rename(columns={'stationName': 'name', 'lat': 'latitude', 'long': 'longitude'})

    unique_stations = list(set(df['Departure Station'].unique()) | set(df['Arrival Destination'].unique()))

    station_names = stations['name'].tolist()
    mapping = {}
    unmatched = []

    for s in unique_stations:
        res = process.extractOne(s, station_names, scorer=fuzz.WRatio)
        if res and res[1] >= 85:
            mapping[s] = res[0]
        else:
            unmatched.append(s)

    with open('data/processed/unmatched_stations.txt', 'w') as f:
        for u in unmatched:
            f.write(f"{u}\n")

    # Map matched names
    df_encoded['Departure_Mapped'] = df_encoded['Departure Station'].map(mapping)
    df_encoded['Arrival_Mapped'] = df_encoded['Arrival Destination'].map(mapping)

    # Merge lat/lon
    stations_sub = stations[['name', 'latitude', 'longitude']]

    df_encoded = pd.merge(df_encoded, stations_sub, left_on='Departure_Mapped', right_on='name', how='left')
    df_encoded = df_encoded.rename(columns={'latitude': 'departure_lat', 'longitude': 'departure_lon'}).drop(columns=['name'])

    df_encoded = pd.merge(df_encoded, stations_sub, left_on='Arrival_Mapped', right_on='name', how='left')
    df_encoded = df_encoded.rename(columns={'latitude': 'arrival_lat', 'longitude': 'arrival_lon'}).drop(columns=['name'])

    # Haversine distance
    def calc_dist(row):
        if pd.notnull(row['departure_lat']) and pd.notnull(row['departure_lon']) and pd.notnull(row['arrival_lat']) and pd.notnull(row['arrival_lon']):
            return haversine((row['departure_lat'], row['departure_lon']), (row['arrival_lat'], row['arrival_lon']), unit=Unit.KILOMETERS)
        return np.nan

    df_encoded['haversine_distance_km'] = df_encoded.apply(calc_dist, axis=1)

    # Drop rows without distance or other continuous features
    df_encoded = df_encoded.dropna(subset=['haversine_distance_km', 'advance_booking_days', 'scheduled_journey_duration_mins', 'hour_of_departure', 'hour_of_purchase'])

    # Figure 6: Pairplot
    cols_pairplot = ['advance_booking_days', 'haversine_distance_km', 'scheduled_journey_duration_mins', 'price_gbp']
    sample_df = df_encoded[cols_pairplot].dropna().sample(min(2000, len(df_encoded)))
    pairplot = sns.pairplot(sample_df)
    pairplot.fig.suptitle('Figure 6: Pairplot: booking days, distance, duration, price. Source: 2024 National Rail Ticket Data (Maven Analytics).', y=1.02, wrap=True)
    pairplot.savefig('outputs/figures/figure_06.png', dpi=300)
    plt.close()

    # StandardScaler
    continuous_features = ['advance_booking_days', 'haversine_distance_km', 'scheduled_journey_duration_mins', 'hour_of_departure', 'hour_of_purchase']
    scaler = StandardScaler()

    for c in continuous_features:
        df_encoded[c + '_raw'] = df_encoded[c]

    df_encoded[continuous_features] = scaler.fit_transform(df_encoded[continuous_features])

    import joblib
    joblib.dump(scaler, 'outputs/models/scaler.pkl')

    # Figure 1: Correlation heatmap of all numeric features vs price_gbp
    numeric_cols = df_encoded.select_dtypes(include=[np.number]).columns
    corr = df_encoded[numeric_cols].corr()

    plt.figure(figsize=(15, 12))
    sns.heatmap(corr[['price_gbp']].sort_values(by='price_gbp', ascending=False), annot=False, cmap='coolwarm')
    plt.title('Figure 1: Correlation heatmap, numeric features vs price_gbp. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_01.png', dpi=300)
    plt.close()

    df_encoded.to_csv('data/processed/features_full.csv', index=False)
    print("Feature engineering complete.")

if __name__ == '__main__':
    create_features()
