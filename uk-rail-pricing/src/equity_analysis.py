import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os

def run_equity_analysis():
    os.makedirs('uk-rail-pricing/outputs/figures', exist_ok=True)
    os.makedirs('uk-rail-pricing/outputs/tables', exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

    import data_loader
    orig_df = data_loader.load_and_clean_data("uk-rail-pricing/data/raw/railway.csv")
    orig_df['price_gbp'] = pd.to_numeric(orig_df['Price'], errors='coerce')
    orig_df = orig_df.dropna(subset=['price_gbp']).reset_index(drop=True)
    orig_df = orig_df.sort_values('transaction_datetime').reset_index(drop=True)

    preds_df = pd.read_csv('uk-rail-pricing/data/processed/predictions_full.csv')
    orig_df['predicted_price'] = preds_df['predicted_price']

    # Needs haversine distance, we can merge it from features_full but before scaling... Wait, features_full has scaled haversine.
    # Recompute haversine for equity analysis to be safe, or just use the unscaled version if available.
    # The prompt says: "Equity impact matrix — scatter of haversine_distance_km vs. predicted price, colour-coded by has_railcard"
    # We will recompute it.
    stations_df = pd.read_csv("uk-rail-pricing/data/geospatial/stations.csv")
    station_map = dict(zip(stations_df['stationName'], zip(stations_df['lat'], stations_df['long'])))

    # We will use simple mapping for plotting purposes (might miss a few due to fuzzy, but that's fine for the scatter)
    def get_dist(row):
        from haversine import haversine
        dep = station_map.get(row['Departure Station'])
        arr = station_map.get(row['Arrival Destination'])
        if dep and arr:
            return haversine(dep, arr)
        return np.nan

    orig_df['haversine_distance_km'] = orig_df.apply(get_dist, axis=1)
    orig_df['has_railcard'] = (orig_df['Railcard'] != 'None').astype(int)

    # 4. Equity constraint: Cap predicted_price at no more than the standard Off-Peak fare for Senior/Disabled
    # We can approximate standard off-peak by taking the max off-peak fare for that route, or just capping at current price if it's off-peak.
    # The prompt: "cap predictions at no more than the standard Off-Peak fare for any transaction where Railcard is Senior or Disabled"
    # We find the route's average off-peak fare as proxy, or if we can't find it, we cap at the current price if the current ticket is off-peak.
    off_peak_fares = orig_df[orig_df['Ticket Type'] == 'Off-Peak'].groupby(['Departure Station', 'Arrival Destination'])['price_gbp'].mean().reset_index()
    off_peak_fares.rename(columns={'price_gbp': 'route_off_peak'}, inplace=True)
    orig_df = orig_df.merge(off_peak_fares, on=['Departure Station', 'Arrival Destination'], how='left')

    def cap_price(row):
        if row['Railcard'] in ['Senior', 'Disabled']:
            cap = row['route_off_peak'] if pd.notna(row['route_off_peak']) else row['price_gbp']
            return min(row['predicted_price'], cap)
        return row['predicted_price']

    orig_df['predicted_price_capped'] = orig_df.apply(cap_price, axis=1)

    # Figure 17: Boxplot of algorithmic predicted price vs actual discounted price, faceted by railcard tier
    plt.figure(figsize=(10, 6))
    plot_data = pd.melt(orig_df, id_vars=['Railcard'], value_vars=['price_gbp', 'predicted_price_capped'], var_name='Price Type', value_name='Fare')
    plot_data['Price Type'] = plot_data['Price Type'].map({'price_gbp': 'Actual Price', 'predicted_price_capped': 'Algorithmic Price (Capped)'})

    plt_sns.boxplot(data=plot_data, x='Railcard', y='Fare', hue='Price Type')
    plt.title('Figure 17: Algorithmic vs Actual Price by Railcard Tier\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_17.png')
    plt.close()

    # Figure 18: Equity impact matrix
    plt.figure(figsize=(10, 6))
    plt_sns.scatterplot(data=orig_df, x='haversine_distance_km', y='predicted_price_capped', hue='has_railcard', alpha=0.5)
    plt.title('Figure 18: Equity Impact Matrix (Distance vs Predicted Price)\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_18.png')
    plt.close()

    # Table 5: Equity Risk Routes
    orig_df['route'] = orig_df['Departure Station'] + " -> " + orig_df['Arrival Destination']
    equity_risk_df = orig_df[orig_df['Railcard'].isin(['Senior', 'Disabled'])].groupby(['route', 'Railcard']).agg(
        Avg_Current_Price=('price_gbp', 'mean'),
        Avg_Predicted_Price=('predicted_price', 'mean') # use uncapped to see the risk before cap
    ).reset_index()

    equity_risk_df['% Increase'] = (equity_risk_df['Avg_Predicted_Price'] - equity_risk_df['Avg_Current_Price']) / equity_risk_df['Avg_Current_Price'] * 100
    equity_risk_df['Risk Level'] = equity_risk_df['% Increase'].apply(lambda x: 'High' if x > 15 else ('Medium' if x > 5 else 'Low'))

    high_risk_routes = equity_risk_df[equity_risk_df['% Increase'] > 15].sort_values('% Increase', ascending=False)
    high_risk_routes.rename(columns={'Railcard': 'Railcard Tier', 'Avg_Current_Price': 'Avg Current Price', 'Avg_Predicted_Price': 'Avg Predicted Price'}, inplace=True)
    high_risk_routes.to_csv('uk-rail-pricing/outputs/tables/equity_risk_routes.csv', index=False)

if __name__ == "__main__":
    run_equity_analysis()
