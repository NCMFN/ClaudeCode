import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os

def run_anomaly_detection():
    os.makedirs('uk-rail-pricing/outputs/figures', exist_ok=True)
    os.makedirs('uk-rail-pricing/outputs/tables', exist_ok=True)
    plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

    # Load original data and predictions
    import data_loader
    orig_df = data_loader.load_and_clean_data("uk-rail-pricing/data/raw/railway.csv")
    orig_df['price_gbp'] = pd.to_numeric(orig_df['Price'], errors='coerce')
    orig_df = orig_df.dropna(subset=['price_gbp']).reset_index(drop=True)

    # Sort just like in model.py
    orig_df = orig_df.sort_values('transaction_datetime').reset_index(drop=True)

    preds_df = pd.read_csv('uk-rail-pricing/data/processed/predictions_full.csv')
    orig_df['predicted_price'] = preds_df['predicted_price']

    # Compute residuals
    orig_df['residual'] = orig_df['price_gbp'] - orig_df['predicted_price']

    # Flag anomalies
    mean_res = orig_df['residual'].mean()
    std_res = orig_df['residual'].std()
    upper_bound = mean_res + 2 * std_res
    lower_bound = mean_res - 2 * std_res

    orig_df['is_anomaly'] = ((orig_df['residual'] > upper_bound) | (orig_df['residual'] < lower_bound)).astype(int)

    # Analyze by Reason for Delay (Disruption type)
    disruption_stats = orig_df.groupby('Reason for Delay').agg(
        total_tx=('Transaction ID', 'count'),
        anomaly_count=('is_anomaly', 'sum'),
        mean_residual=('residual', 'mean')
    ).reset_index()
    disruption_stats['anomaly_rate'] = disruption_stats['anomaly_count'] / disruption_stats['total_tx']

    # Table 3
    disruption_stats.to_csv('uk-rail-pricing/outputs/tables/anomaly_by_disruption_type.csv', index=False)

    # Figure 15: Time-series plot of daily average residual magnitude with disruption events
    orig_df['journey_date'] = orig_df['journey_datetime'].dt.date
    daily_res = orig_df.groupby('journey_date')['residual'].apply(lambda x: x.abs().mean()).reset_index()

    plt.figure(figsize=(12, 6))
    plt_sns.lineplot(data=daily_res, x='journey_date', y='residual')
    # Add vertical line for ASLEF strike 2024-03-01
    strike_date = pd.to_datetime('2024-03-01').date()
    if strike_date in daily_res['journey_date'].values:
        plt.axvline(x=strike_date, color='red', linestyle='--', label='ASLEF Strike')
        plt.legend()

    plt.title('Figure 15: Daily Average Residual Magnitude\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xlabel('Journey Date')
    plt.ylabel('Average Absolute Residual (GBP)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_15.png')
    plt.close()

    # Figure 16: Stacked bar chart — anomaly rate by Reason for Delay
    plt.figure(figsize=(10, 6))
    plt_sns.barplot(data=disruption_stats.sort_values('anomaly_rate', ascending=False), x='Reason for Delay', y='anomaly_rate')
    plt.title('Figure 16: Anomaly Rate by Disruption Type\nSource: 2024 National Rail Ticket Data (Maven Analytics).')
    plt.xticks(rotation=45)
    plt.ylabel('Anomaly Rate')
    plt.tight_layout()
    plt.savefig('uk-rail-pricing/outputs/figures/Figure_16.png')
    plt.close()

    # Table 4: Human Intervention Nodes
    # Identify routes/stations with the highest persistent anomaly rate
    node_stats = orig_df.groupby('Departure Station').agg(
        total_tx=('Transaction ID', 'count'),
        anomaly_count=('is_anomaly', 'sum'),
        mean_res=('residual', 'mean')
    ).reset_index()
    node_stats['anomaly_rate'] = node_stats['anomaly_count'] / node_stats['total_tx']

    # Get primary disruption type per station for anomalies
    anomalies_only = orig_df[orig_df['is_anomaly'] == 1]
    if not anomalies_only.empty:
        primary_disruptions = anomalies_only.groupby('Departure Station')['Reason for Delay'].apply(lambda x: x.mode()[0] if not x.mode().empty else 'None').reset_index()
        node_stats = node_stats.merge(primary_disruptions, on='Departure Station', how='left')
    else:
        node_stats['Reason for Delay'] = 'None'

    node_stats.rename(columns={'Departure Station': 'Station', 'Reason for Delay': 'Primary Disruption Type', 'mean_res': 'Avg Revenue Deficit per Event'}, inplace=True)

    # Filter for nodes with high enough volume
    intervention_nodes = node_stats[node_stats['total_tx'] > 10].sort_values('anomaly_rate', ascending=False).head(20)
    intervention_nodes.to_csv('uk-rail-pricing/outputs/tables/human_intervention_nodes.csv', index=False)

if __name__ == "__main__":
    run_anomaly_detection()
