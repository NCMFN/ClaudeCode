import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import folium
from branca.colormap import LinearColormap
import os

STYLE = {
    'primary': '#2E5EAA',
    'secondary': '#D9534F'
}

def analyze_equity_and_elasticity():
    os.makedirs('outputs/tables', exist_ok=True)
    os.makedirs('outputs/figures', exist_ok=True)

    df = pd.read_csv('data/processed/features_full_with_preds.csv')

    # 7. Equity & Vulnerable Demographics Analysis
    off_peak_fares = df[df['Ticket Type_Off-Peak'] == True].groupby('Route')['price_gbp'].mean().to_dict()

    def apply_equity_cap(row):
        pred = row['predicted_price']
        if row['Railcard'] in ['Senior', 'Disabled']:
            cap = off_peak_fares.get(row['Route'], row['price_gbp'])
            return min(pred, cap)
        return pred

    df['predicted_price_capped'] = df.apply(apply_equity_cap, axis=1)

    df['pct_increase'] = ((df['predicted_price_capped'] - df['price_gbp']) / df['price_gbp']) * 100

    plot_df = pd.melt(df, id_vars=['Railcard'], value_vars=['price_gbp', 'predicted_price_capped'], var_name='Price Type', value_name='Price_Value')

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=plot_df, x='Railcard', y='Price_Value', hue='Price Type', palette='Set2')
    plt.title('Figure 43: Predicted vs actual price by railcard tier (boxplot). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_43.png', dpi=300)
    plt.close()

    tiers = ['None', 'Adult', 'Senior', 'Disabled']
    for i, tier in enumerate(tiers):
        plt.figure(figsize=(6, 5))
        tier_data = plot_df[plot_df['Railcard'] == tier]
        sns.boxplot(data=tier_data, x='Price Type', y='Price_Value', palette='Set1')
        plt.title(f'Figure {44+i}: Predicted vs actual price, {tier} tier (boxplot). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
        plt.tight_layout()
        plt.savefig(f'outputs/figures/figure_{44+i}.png', dpi=300)
        plt.close()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df.sample(min(10000, len(df))), x='haversine_distance_km_raw', y='predicted_price_capped', hue='has_railcard', alpha=0.5)
    plt.title('Figure 48: Equity impact matrix (distance vs price, by has_railcard). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_48.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(df[df['Railcard'] == 'Senior']['pct_increase'], bins=50, color='purple')
    plt.title('Figure 49: % price increase distribution, Senior Railcard (hist). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_49.png', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(df[df['Railcard'] == 'Disabled']['pct_increase'], bins=50, color='green')
    plt.title('Figure 50: % price increase distribution, Disabled Railcard (hist). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_50.png', dpi=300)
    plt.close()

    vuln_df = df[df['Railcard'].isin(['Senior', 'Disabled'])]
    risk_routes = vuln_df.groupby(['Route', 'Railcard']).agg(
        Avg_Current_Price=('price_gbp', 'mean'),
        Avg_Predicted_Price=('predicted_price_capped', 'mean')
    ).reset_index()

    risk_routes['Pct_Increase'] = ((risk_routes['Avg_Predicted_Price'] - risk_routes['Avg_Current_Price']) / risk_routes['Avg_Current_Price']) * 100
    risk_routes = risk_routes[risk_routes['Pct_Increase'] > 15].copy()
    risk_routes['Risk Level'] = pd.cut(risk_routes['Pct_Increase'], bins=[15, 30, 50, float('inf')], labels=['Moderate', 'High', 'Severe'])

    risk_routes.columns = ['Route', 'Railcard Tier', 'Avg Current Price', 'Avg Predicted Price', '% Increase', 'Risk Level']
    risk_routes.to_csv('outputs/tables/equity_risk_routes.csv', index=False)

    # 8. Route-Level Network Elasticity Analysis
    route_stats = df.groupby('Route').agg(
        Mean_Price=('price_gbp', 'mean'),
        Std_Price=('price_gbp', 'std'),
        Volume=('price_gbp', 'count')
    ).reset_index()

    route_stats = route_stats[route_stats['Volume'] > 5].copy()
    route_stats['Elasticity'] = route_stats['Std_Price'] / route_stats['Mean_Price']

    route_stats['Classification'] = pd.qcut(route_stats['Elasticity'].fillna(0), q=3, labels=['Low Elasticity', 'Medium Elasticity', 'High Elasticity'], duplicates='drop')

    route_stats = route_stats[['Route', 'Mean_Price', 'Std_Price', 'Elasticity', 'Volume', 'Classification']]
    route_stats.columns = ['Route', 'Mean Price', 'Std Price', 'Elasticity', 'Volume', 'Classification']
    route_stats.to_csv('outputs/tables/route_elasticity_table.csv', index=False)

    plt.figure(figsize=(10, 6))
    route_stats['Revenue'] = route_stats['Mean Price'] * route_stats['Volume']
    sns.scatterplot(data=route_stats, x='Volume', y='Elasticity', size='Revenue', sizes=(20, 500), alpha=0.5, color=STYLE['primary'])
    plt.title('Figure 51: Route elasticity vs volume (bubble = revenue). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_51.png', dpi=300)
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.histplot(route_stats['Elasticity'], bins=50, color=STYLE['secondary'])
    plt.title('Figure 52: Route elasticity distribution (hist). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_52.png', dpi=300)
    plt.close()

    top_el = route_stats.sort_values(by='Elasticity', ascending=False).head(20)
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_el, y='Route', x='Elasticity', color=STYLE['primary'])
    plt.title('Figure 53: Top 20 highest-elasticity routes (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_53.png', dpi=300)
    plt.close()

    df['month'] = pd.to_datetime(df['transaction_datetime']).dt.month
    monthly_el = df.groupby(['Route', 'month'])['price_gbp'].agg(['mean', 'std']).reset_index()
    monthly_el['elasticity'] = monthly_el['std'] / monthly_el['mean']
    monthly_avg = monthly_el.groupby('month')['elasticity'].mean()

    plt.figure(figsize=(8, 6))
    plt.plot(monthly_avg.index, monthly_avg.values, marker='o', color=STYLE['primary'])
    plt.title('Figure 54: Monthly elasticity trend, Jan-Apr (line). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xticks([1, 2, 3, 4], ['Jan', 'Feb', 'Mar', 'Apr'])
    plt.xlabel('Month')
    plt.ylabel('Average Network Elasticity')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_54.png', dpi=300)
    plt.close()

    dep_stats = df.groupby('Departure Station').agg(
        lat=('departure_lat', 'first'),
        lon=('departure_lon', 'first')
    ).reset_index().dropna()

    dep_el = df.groupby('Departure Station')['price_gbp'].agg(['mean', 'std']).reset_index()
    dep_el['elasticity'] = dep_el['std'] / dep_el['mean']

    map_data = pd.merge(dep_stats, dep_el, on='Departure Station')
    map_data = map_data.dropna(subset=['elasticity'])

    m = folium.Map(location=[54.0, -2.5], zoom_start=6)
    if not map_data.empty:
        colormap = LinearColormap(colors=['green', 'yellow', 'red'], vmin=map_data['elasticity'].min(), vmax=map_data['elasticity'].max())
        colormap.add_to(m)

        for idx, row in map_data.iterrows():
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=5,
                popup=f"{row['Departure Station']}: {row['elasticity']:.2f}",
                color=colormap(row['elasticity']),
                fill=True,
                fill_opacity=0.7
            ).add_to(m)

    m.save('outputs/figures/elasticity_map.html')

    import geopandas as gpd
    if not map_data.empty:
        gdf = gpd.GeoDataFrame(map_data, geometry=gpd.points_from_xy(map_data.lon, map_data.lat))
        try:
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            uk = world[world.name == "United Kingdom"]

            fig, ax = plt.subplots(figsize=(8, 10))
            uk.plot(ax=ax, color='lightgrey')
            gdf.plot(ax=ax, column='elasticity', cmap='RdYlGn_r', legend=True, markersize=20, alpha=0.7)
            plt.title('Figure 55: Elasticity map (folium/geopandas, static PNG export). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
            plt.axis('off')
            plt.tight_layout()
            plt.savefig('outputs/figures/figure_55.png', dpi=300)
            plt.close()
        except:
            # Fallback if naturalearth dataset fails
            fig, ax = plt.subplots(figsize=(8, 10))
            gdf.plot(ax=ax, column='elasticity', cmap='RdYlGn_r', legend=True, markersize=20, alpha=0.7)
            plt.title('Figure 55: Elasticity map (folium/geopandas, static PNG export). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
            plt.axis('off')
            plt.tight_layout()
            plt.savefig('outputs/figures/figure_55.png', dpi=300)
            plt.close()

    print("Equity and Elasticity analysis complete.")

if __name__ == '__main__':
    analyze_equity_and_elasticity()
