import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os

def run_eda():
    os.makedirs('uk-rail-pricing/outputs/figures', exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

    # Load original data to keep original column names and non-scaled values for easier interpretation
    import data_loader
    df = data_loader.load_and_clean_data("uk-rail-pricing/data/raw/railway.csv")
    df['price_gbp'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['price_gbp'])

    # Station Volume Analysis: Figure 4
    plt.figure(figsize=(12, 6))
    top_stations = df['Departure Station'].value_counts().head(30)
    plt_sns.barplot(x=top_stations.index, y=top_stations.values, color='#1f77b4')
    plt.xticks(rotation=90)
    plt.title('Figure 4: Top 30 Busiest Departure Stations\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.ylabel('Transaction Volume')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_4.png')
    plt.close()

    # Temporal Price Patterns: Figure 5
    plt.figure(figsize=(10, 6))
    pivot = pd.pivot_table(df, values='price_gbp', index='day_of_week', columns='hour_of_purchase', aggfunc='mean')
    plt_sns.heatmap(pivot, cmap='YlGnBu')
    plt.title('Figure 5: Average Price by Hour of Purchase and Day of Week\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_5.png')
    plt.close()

    # Railcard Equity Analysis: Figure 6
    plt.figure(figsize=(10, 6))
    plt_sns.boxplot(data=df, x='Railcard', y='price_gbp')
    plt.title('Figure 6: Price Paid Across Railcard Tiers\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_6.png')
    plt.close()

    # Route-Level Elasticity: Figure 7
    plt.figure(figsize=(10, 6))
    df['route'] = df['Departure Station'] + " -> " + df['Arrival Destination']
    route_stats = df.groupby('route')['price_gbp'].agg(['mean', 'std', 'count']).dropna()
    route_stats = route_stats[route_stats['count'] > 50] # Filter low volume
    plt_sns.scatterplot(data=route_stats, x='mean', y='std', size='count', alpha=0.5)
    plt.title('Figure 7: Route-Level Price Variance\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xlabel('Mean Price (GBP)')
    plt.ylabel('Standard Deviation of Price')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_7.png')
    plt.close()

    # Disruption Overlay: Figure 8
    # Using hardcoded dates as mentioned in prompt
    df['journey_date_only'] = df['journey_datetime'].dt.date
    strike_date = pd.to_datetime('2024-03-01').date()
    df['is_strike_day'] = (df['journey_date_only'] == strike_date)

    plt.figure(figsize=(8, 6))
    plt_sns.barplot(data=df, x='is_strike_day', y='price_gbp', errorbar='sd')
    plt.title('Figure 8: Average Price on Disruption vs Non-Disruption Days\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xticks([0, 1], ['Non-Disruption', 'Disruption (Strike Day)'])
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_8.png')
    plt.close()

if __name__ == "__main__":
    run_eda()
