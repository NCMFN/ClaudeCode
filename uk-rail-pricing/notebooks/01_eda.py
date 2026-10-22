import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

STYLE = {
    'primary': '#2E5EAA',
    'secondary': '#D9534F'
}

def generate_eda_figures():
    df = pd.read_csv('data/processed/features_full.csv')
    os.makedirs('outputs/figures', exist_ok=True)

    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    df['journey_datetime'] = pd.to_datetime(df['journey_datetime'])
    df['Date of Journey'] = pd.to_datetime(df['Date of Journey'], format='%d/%m/%Y', errors='coerce')

    # Reconstruct original categorical features that were OHE
    def get_railcard(row):
        if row['Railcard_Adult']: return 'Adult'
        if row['Railcard_Senior']: return 'Senior'
        if row['Railcard_Disabled']: return 'Disabled'
        return 'None'

    def get_ticket_class(row):
        if row['Ticket Class_First Class']: return 'First Class'
        return 'Standard'

    def get_ticket_type(row):
        if row['Ticket Type_Advance']: return 'Advance'
        if row['Ticket Type_Anytime']: return 'Anytime'
        return 'Off-Peak'

    df['Railcard'] = df.apply(get_railcard, axis=1)
    df['Ticket Class'] = df.apply(get_ticket_class, axis=1)
    df['Ticket Type'] = df.apply(get_ticket_type, axis=1)

    # 7
    plt.figure(figsize=(14, 8))
    top_departures = df['Departure Station'].value_counts().head(30)
    sns.barplot(y=top_departures.index, x=top_departures.values, color=STYLE['primary'])
    plt.title('Figure 7: Top 30 busiest departure stations (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Transaction Count')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_07.png', dpi=300)
    plt.close()

    # 8
    pivot_price = df.pivot_table(index='day_of_week', columns='hour_of_purchase_raw', values='price_gbp', aggfunc='mean')
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_price, cmap='YlGnBu')
    plt.title('Figure 8: Avg price by hour x day-of-week (heatmap). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_08.png', dpi=300)
    plt.close()

    # 9
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Railcard', y='price_gbp', palette='Set2')
    plt.title('Figure 9: Price by railcard tier (boxplot). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_09.png', dpi=300)
    plt.close()

    # 10
    df['Route'] = df['Departure Station'] + " -> " + df['Arrival Destination']
    route_stats = df.groupby('Route')['price_gbp'].agg(['mean', 'std', 'count'])
    route_stats['variance'] = route_stats['std'] ** 2
    top_variance = route_stats[route_stats['count'] > 10].sort_values(by='variance', ascending=False).head(20)

    plt.figure(figsize=(12, 8))
    sns.barplot(y=top_variance.index, x=top_variance['variance'], color=STYLE['secondary'])
    plt.title('Figure 10: Route-level price variance (high-variance flagged). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Price Variance')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_10.png', dpi=300)
    plt.close()

    # 11
    strike_dates = pd.to_datetime(['2024-03-01', '2024-01-30', '2024-02-05', '2024-04-05', '2024-04-08'])
    df['is_disruption_day'] = df['Date of Journey'].isin(strike_dates) | (~df['Reason for Delay_NA'])

    plt.figure(figsize=(8, 6))
    sns.barplot(data=df, x='is_disruption_day', y='price_gbp', errorbar=None, palette='pastel')
    plt.title('Figure 11: Avg price: disruption vs non-disruption days. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_11.png', dpi=300)
    plt.close()

    # 12
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='month', y='price_gbp', palette='Blues')
    plt.title('Figure 12: price_gbp by month (boxplot). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_12.png', dpi=300)
    plt.close()

    # 13
    daily_price = df.groupby(df['transaction_datetime'].dt.date)['price_gbp'].mean()
    plt.figure(figsize=(12, 6))
    plt.plot(daily_price.index, daily_price.values, color=STYLE['primary'])
    plt.title('Figure 13: Daily avg price line chart, Jan-Apr. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_13.png', dpi=300)
    plt.close()

    # 14
    plt.figure(figsize=(8, 6))
    sns.countplot(data=df, x='day_of_week', color=STYLE['primary'])
    plt.title('Figure 14: Transaction volume by day of week. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_14.png', dpi=300)
    plt.close()

    # 15
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='hour_of_purchase_raw', color=STYLE['primary'])
    plt.title('Figure 15: Transaction volume by hour of purchase. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_15.png', dpi=300)
    plt.close()

    # 16
    pivot_count = df.pivot_table(index='day_of_week', columns='hour_of_purchase_raw', values='price_gbp', aggfunc='count')
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_count, cmap='Purples')
    plt.title('Figure 16: Transaction count heatmap, hour x day-of-week. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_16.png', dpi=300)
    plt.close()

    # 17
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df.sample(min(10000, len(df))), x='haversine_distance_km_raw', y='price_gbp', hue='Ticket Class', alpha=0.5)
    plt.title('Figure 17: Distance vs price scatter, by ticket class. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_17.png', dpi=300)
    plt.close()

    # 18
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='is_peak', y='price_gbp', palette='Set1')
    plt.title('Figure 18: price_gbp by is_peak flag (boxplot). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_18.png', dpi=300)
    plt.close()

    # 19
    plt.figure(figsize=(14, 8))
    top_arrivals = df['Arrival Destination'].value_counts().head(30)
    sns.barplot(y=top_arrivals.index, x=top_arrivals.values, color=STYLE['secondary'])
    plt.title('Figure 19: Top 30 busiest arrival stations (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Transaction Count')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_19.png', dpi=300)
    plt.close()

    # 20
    route_rev = df.groupby('Route')['price_gbp'].sum().sort_values(ascending=False).head(20)
    plt.figure(figsize=(12, 8))
    sns.barplot(y=route_rev.index, x=route_rev.values, color=STYLE['primary'])
    plt.title('Figure 20: Top 20 highest-revenue routes (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Total Revenue (GBP)')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_20.png', dpi=300)
    plt.close()

    # 21
    route_avg = route_stats[route_stats['count'] > 50].sort_values(by='mean', ascending=False).head(20)
    plt.figure(figsize=(12, 8))
    sns.barplot(y=route_avg.index, x=route_avg['mean'], color=STYLE['primary'])
    plt.title('Figure 21: Top 20 highest-average-price routes (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Average Price (GBP)')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_21.png', dpi=300)
    plt.close()

    # 22
    plt.figure(figsize=(10, 6))
    sns.histplot(df['scheduled_journey_duration_mins_raw'], bins=50, color='teal')
    plt.title('Figure 22: Journey duration histogram. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Duration (mins)')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_22.png', dpi=300)
    plt.close()

    # 23
    delayed = df[df['is_delayed'] == 1]
    plt.figure(figsize=(10, 6))
    sns.histplot(delayed['actual_delay_mins'], bins=50, color=STYLE['secondary'])
    plt.title('Figure 23: Delay minutes histogram (delayed only). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Delay (mins)')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_23.png', dpi=300)
    plt.close()

    # 24
    plt.figure(figsize=(8, 6))
    delay_rate = df.groupby('Ticket Type')['is_delayed'].mean()
    sns.barplot(x=delay_rate.index, y=delay_rate.values, color=STYLE['primary'])
    plt.title('Figure 24: is_delayed rate by ticket type (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.ylabel('Delay Rate')
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_24.png', dpi=300)
    plt.close()

    print("EDA complete.")

if __name__ == '__main__':
    generate_eda_figures()
