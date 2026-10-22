import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

STYLE = {
    'primary': '#2E5EAA',
    'secondary': '#D9534F'
}

def detect_anomalies():
    os.makedirs('outputs/tables', exist_ok=True)
    os.makedirs('outputs/figures', exist_ok=True)

    # We load the dataframe that has the residuals from the test fold
    # Actually, we should compute residuals for the entire dataset using the best DT for full analysis, or just use the test fold.
    # Let's compute for the entire dataset to have a richer set of anomalies.

    df = pd.read_csv('data/processed/features_full.csv')
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    df['Date of Journey'] = pd.to_datetime(df['Date of Journey'], format='%d/%m/%Y', errors='coerce')

    import joblib
    best_dt = joblib.load('outputs/models/dt_regressor.pkl')

    drop_cols = [c for c in df.columns if c.endswith('_raw') or c in [
        'Transaction ID', 'Date of Purchase', 'Time of Purchase', 'Purchase Type', 'Payment Method',
        'Departure Station', 'Arrival Destination', 'Date of Journey', 'Departure Time',
        'Arrival Time', 'Actual Arrival Time', 'Journey Status', 'Refund Request',
        'transaction_datetime', 'journey_datetime', 'Arrival Time DT', 'Actual Arrival DT',
        'Departure_Mapped', 'Arrival_Mapped', 'price_gbp', 'Price'
    ]]

    X = df.drop(columns=drop_cols)
    X = X.select_dtypes(include=[np.number])
    X = X.fillna(X.median())

    y_pred = best_dt.predict(X)
    df['predicted_price'] = y_pred
    df['residual'] = df['price_gbp'] - df['predicted_price']

    # Flag high-residual transactions
    res_mean = df['residual'].mean()
    res_std = df['residual'].std()

    df['is_anomaly'] = (df['residual'] > res_mean + 2*res_std) | (df['residual'] < res_mean - 2*res_std)

    # Reconstruct categorical for plotting
    def get_railcard(row):
        if row['Railcard_Adult']: return 'Adult'
        if row['Railcard_Senior']: return 'Senior'
        if row['Railcard_Disabled']: return 'Disabled'
        return 'None'
    df['Railcard'] = df.apply(get_railcard, axis=1)

    # Reconstruct delay reason
    delay_cols = [c for c in df.columns if c.startswith('Reason for Delay_')]
    def get_delay_reason(row):
        for c in delay_cols:
            if row[c]:
                return c.replace('Reason for Delay_', '')
        return 'NA'
    df['Delay_Reason'] = df.apply(get_delay_reason, axis=1)

    # Merge with ORR data implicitly by checking disruption flags
    strike_dates = pd.to_datetime(['2024-03-01', '2024-01-30', '2024-02-05', '2024-04-05', '2024-04-08'])
    df['is_strike_date'] = df['Date of Journey'].isin(strike_dates)

    # Table 3: anomaly_by_disruption_type.csv
    # Compute anomaly rate per disruption type
    anomaly_rate = df.groupby('Delay_Reason')['is_anomaly'].mean().reset_index()
    anomaly_rate.columns = ['Disruption Type', 'Anomaly Rate']
    anomaly_rate.to_csv('outputs/tables/anomaly_by_disruption_type.csv', index=False)

    # Figure 40: Time-series plot of daily average residual magnitude with disruption event markers
    daily_res = df.groupby(df['transaction_datetime'].dt.date)['residual'].apply(lambda x: np.mean(np.abs(x)))
    plt.figure(figsize=(12, 6))
    plt.plot(daily_res.index, daily_res.values, color=STYLE['primary'])

    for sd in strike_dates:
        if sd.date() in daily_res.index:
            plt.axvline(x=sd.date(), color='red', linestyle='--', alpha=0.5)

    plt.title('Figure 40: Daily avg residual magnitude with disruption markers. Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xlabel('Date')
    plt.ylabel('Avg Absolute Residual')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_40.png', dpi=300)
    plt.close()

    # Figure 41: Stacked bar chart - anomaly rate by Reason for Delay category
    plt.figure(figsize=(12, 6))
    sns.barplot(data=anomaly_rate, x='Disruption Type', y='Anomaly Rate', color=STYLE['secondary'])
    plt.title('Figure 41: Anomaly rate by delay reason (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_41.png', dpi=300)
    plt.close()

    # Figure 42: Bar chart of residual mean and std, grouped by railcard tier
    railcard_res = df.groupby('Railcard')['residual'].agg(['mean', 'std']).reset_index()
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    sns.barplot(data=railcard_res, x='Railcard', y='mean', ax=ax1, color=STYLE['primary'], alpha=0.6, label='Mean')
    sns.pointplot(data=railcard_res, x='Railcard', y='std', ax=ax2, color=STYLE['secondary'], markers='o', label='Std')

    ax1.set_ylabel('Mean Residual')
    ax2.set_ylabel('Std Residual')
    plt.title('Figure 42: Residual mean/std by railcard tier (bar). Source: 2024 National Rail Ticket Data (Maven Analytics).', wrap=True)
    plt.tight_layout()
    plt.savefig('outputs/figures/figure_42.png', dpi=300)
    plt.close()

    # Table 4: human_intervention_nodes.csv
    # Identify routes/stations with the highest persistent anomaly rate
    df['Route'] = df['Departure Station'] + " -> " + df['Arrival Destination']
    route_anom = df.groupby('Route').agg(
        Anomaly_Rate=('is_anomaly', 'mean'),
        Primary_Disruption=('Delay_Reason', lambda x: x.mode()[0] if not x.mode().empty else 'NA'),
        Avg_Revenue_Deficit=('residual', lambda x: x[x > 0].mean() if len(x[x > 0]) > 0 else 0)
    ).reset_index()

    route_anom = route_anom.sort_values(by='Anomaly_Rate', ascending=False).head(50)
    route_anom.columns = ['Station', 'Anomaly Rate', 'Primary Disruption Type', 'Avg Revenue Deficit per Event']
    route_anom.to_csv('outputs/tables/human_intervention_nodes.csv', index=False)

    # Save the dataframe with predictions for equity analysis
    df.to_csv('data/processed/features_full_with_preds.csv', index=False)

    print("Anomaly detection complete.")

if __name__ == '__main__':
    detect_anomalies()
