import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os
import folium

def run_elasticity_analysis():
    os.makedirs('uk-rail-pricing/outputs/figures', exist_ok=True)
    os.makedirs('uk-rail-pricing/outputs/tables', exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

    import data_loader
    df = data_loader.load_and_clean_data("uk-rail-pricing/data/raw/railway.csv")
    df['price_gbp'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['price_gbp']).reset_index(drop=True)

    df['route'] = df['Departure Station'] + " -> " + df['Arrival Destination']

    # Table 6: Route Elasticity
    route_stats = df.groupby('route').agg(
        Mean_Price=('price_gbp', 'mean'),
        Std_Price=('price_gbp', 'std'),
        Volume=('Transaction ID', 'count'),
        Departure_Station=('Departure Station', 'first')
    ).reset_index()

    # Filter low volume
    route_stats = route_stats[route_stats['Volume'] > 30]

    route_stats['Elasticity'] = route_stats['Std_Price'] / route_stats['Mean_Price']

    # Classify Elasticity
    q33 = route_stats['Elasticity'].quantile(0.33)
    q66 = route_stats['Elasticity'].quantile(0.66)

    def classify(e):
        if e <= q33: return 'Low Elasticity'
        elif e <= q66: return 'Medium Elasticity'
        else: return 'High Elasticity'

    route_stats['Classification'] = route_stats['Elasticity'].apply(classify)

    # Save Table 6
    out_table = route_stats[['route', 'Mean_Price', 'Std_Price', 'Elasticity', 'Volume', 'Classification']].copy()
    out_table.rename(columns={'route': 'Route', 'Mean_Price': 'Mean Price', 'Std_Price': 'Std Price'}, inplace=True)
    out_table.to_csv('uk-rail-pricing/outputs/tables/route_elasticity_table.csv', index=False)

    # Figure 19: Scatter plot of route elasticity vs volume
    plt.figure(figsize=(10, 6))
    plt_sns.scatterplot(data=route_stats, x='Volume', y='Elasticity', hue='Classification', size='Mean_Price', sizes=(20, 200), alpha=0.7)
    plt.title('Figure 19: Route Elasticity vs Volume\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xlabel('Transaction Volume')
    plt.ylabel('Price Elasticity (Std/Mean)')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_19.png')
    plt.close()

    # Figure 20: Choropleth-style map using folium
    stations_df = pd.read_csv("uk-rail-pricing/data/geospatial/stations.csv")
    station_map = dict(zip(stations_df['stationName'], zip(stations_df['lat'], stations_df['long'])))

    from rapidfuzz import process, fuzz
    station_names = stations_df['stationName'].unique()
    match_cache = {}
    def get_best_match(name):
        if name in match_cache: return match_cache[name]
        if name in station_names:
            match_cache[name] = name
            return name
        match = process.extractOne(name, station_names, scorer=fuzz.WRatio, score_cutoff=85)
        res = match[0] if match else None
        match_cache[name] = res
        return res

    route_stats['dep_match'] = route_stats['Departure_Station'].apply(get_best_match)

    m = folium.Map(location=[54.0, -2.0], zoom_start=6)

    colors = {'Low Elasticity': 'green', 'Medium Elasticity': 'orange', 'High Elasticity': 'red'}

    for idx, row in route_stats.iterrows():
        st_match = row['dep_match']
        if st_match and st_match in station_map:
            lat, lon = station_map[st_match]
            if pd.notna(lat) and pd.notna(lon):
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=5,
                    popup=f"{row['route']}: {row['Classification']}",
                    color=colors.get(row['Classification'], 'gray'),
                    fill=True,
                    fill_color=colors.get(row['Classification'], 'gray')
                ).add_to(m)

    m.save('uk-rail-pricing/outputs/figures/elasticity_map.html')

if __name__ == "__main__":
    run_elasticity_analysis()
