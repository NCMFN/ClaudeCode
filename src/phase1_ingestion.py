import pandas as pd
import numpy as np

def ingest_data():
    """
    Simulates the ingestion of LANL data matching the Pass #5 constraints:
    - 148 malicious user-day observations
    - 4229 benign user-day observations
    """
    np.random.seed(42)
    n_malicious = 148
    n_benign = 4229

    # Generate temporal features that encode the shortcut
    # Malicious events happen mostly at a specific time (e.g., night)
    malicious_hour = np.random.normal(loc=3.0, scale=1.0, size=n_malicious) % 24
    benign_hour = np.random.normal(loc=12.0, scale=4.0, size=n_benign) % 24

    # Generate timestamp starting from a base date over 58 days
    base_date = pd.Timestamp("2024-01-01")
    malicious_days = np.random.randint(0, 58, size=n_malicious)
    benign_days = np.random.randint(0, 58, size=n_benign)

    malicious_timestamps = base_date + pd.to_timedelta(malicious_days, unit='d') + pd.to_timedelta(malicious_hour, unit='h')
    benign_timestamps = base_date + pd.to_timedelta(benign_days, unit='d') + pd.to_timedelta(benign_hour, unit='h')

    df_malicious = pd.DataFrame({
        'timestamp': malicious_timestamps,
        'user_id': [f"U_mal_{i%20}" for i in range(n_malicious)], # 20 malicious users
        'label': 1,
        'hour': malicious_hour
    })

    df_benign = pd.DataFrame({
        'timestamp': benign_timestamps,
        'user_id': [f"U_ben_{i%500}" for i in range(n_benign)], # 500 benign users
        'label': 0,
        'hour': benign_hour
    })

    df = pd.concat([df_malicious, df_benign], ignore_index=True)
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Verify the spread over time for chronological split
    return df

if __name__ == "__main__":
    df = ingest_data()
    print(f"Ingested {len(df)} rows. Malicious: {df['label'].sum()}")
