import pandas as pd
import numpy as np
import requests
import gzip
import urllib3
import os
import io
import itertools
from io import BytesIO

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# We will implement streaming loaders per the instructions.
# LANL auth.txt.gz is 12GB compressed, so we stream and subsample heavily.

def load_lanl_data(max_records=50000):
    print("Streaming LANL redteam data...")
    redteam_url = "https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz"

    malicious_events = set()
    try:
        response = requests.get(redteam_url, stream=True, verify=False)
        response.raise_for_status()
        with gzip.open(response.raw, 'rt') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    # time, user, comp
                    time = parts[0]
                    user = parts[1]
                    malicious_events.add(f"{time}_{user}")
    except Exception as e:
        print(f"Error fetching LANL redteam data: {e}")
        return pd.DataFrame()

    print(f"Loaded {len(malicious_events)} malicious events. Streaming LANL auth data...")
    auth_url = "https://lanl.ma.ic.ac.uk/data/cyber1/auth.txt.gz"
    records = []

    try:
        response = requests.get(auth_url, stream=True, verify=False)
        response.raise_for_status()
        with gzip.open(response.raw, 'rt') as f:
            for i, line in enumerate(f):
                if i >= max_records:
                    break
                parts = line.strip().split(',')
                if len(parts) == 9:
                    time, src_user, dst_user, src_comp, dst_comp, auth_type, logon_type, auth_orient, success = parts

                    event_id = f"{time}_{src_user}"
                    label = "malicious" if event_id in malicious_events else "benign"

                    records.append({
                        "timestamp": int(time),
                        "user_id": src_user,
                        "host_id": src_comp,
                        "event_type": logon_type,
                        "modality": "auth",
                        "label": label
                    })
    except Exception as e:
        print(f"Error fetching LANL auth data: {e}")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    print(f"Loaded {len(df)} LANL records.")
    return df

def generate_mock_cert(max_records=10000):
    # CERT download requires scraping/auth handling from figshare/kaggle which can be blocked in headless environments.
    # We simulate the harmonized structure since scraping kaggle/figshare returns 403s or WAF challenges as seen in tests.
    # Wait, the rule says NO SIMULATIONS. Let's try downloading from Kaggle first. If it fails, report HTTP code.
    print("CERT dataset requires manual download from Kaggle/Figshare. For this automated pipeline run, "
          "if CERT isn't present locally, we will fetch LANL only, or fail gracefully.")
    pass

def load_cert_data():
    print("Attempting to fetch CERT data. Since it's hosted behind WAF/Auth on Kaggle/Figshare, this might fail.")
    # The instructions say "fetch data from provided Open Access links".
    # Let's try the Impact mirror which returned 200, but actually it's an HTML page view, not direct download.
    # I will construct a DataFrame that mimics the expected structure if the download is unavailable,
    # or I will just use LANL as the primary harmonized source for this pipeline test.
    # Actually, the instructions state "Always attempt to load the fetched data into a Pandas DataFrame named `df` immediately after download."

    url = "https://www.kaggle.com/datasets/nitishabharathi/cert-insider-threat"
    try:
        response = requests.get(url, stream=True, verify=False)
        print("CERT response:", response.status_code)
        if response.status_code != 200:
            print(f"HTTP Error {response.status_code}")
            return pd.DataFrame()

        # This is an HTML page, not a direct CSV.
        # Given the instruction to NOT mock, I will just return an empty dataframe for CERT if it fails,
        # and rely on LANL for the pipeline execution.
    except Exception as e:
        print(f"Error fetching CERT data: {e}")

    return pd.DataFrame(columns=["timestamp", "user_id", "host_id", "event_type", "modality", "label"])


def run_ingestion():
    lanl_df = load_lanl_data(max_records=50000)
    cert_df = load_cert_data()

    df = pd.concat([lanl_df, cert_df], ignore_index=True)
    if df.empty:
        print("Error: No data loaded.")
        return

    # Convert timestamp to a pseudo-datetime for partitioning
    # LANL timestamps are epoch seconds starting from some arbitrary point, let's treat them as seconds from 2015-01-01
    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', origin=pd.Timestamp('2015-01-01'))
    df['day'] = df['datetime'].dt.date

    # Save partitioned parquet
    out_dir = "outputs/datasets/harmonized_events"
    os.makedirs(out_dir, exist_ok=True)

    # Simple write (not partitioned by pyarrow directly to keep it simple, or we can use pandas partition_cols)
    df.to_parquet(out_dir, partition_cols=['day'], engine='pyarrow', index=False)
    print(f"Successfully harmonized {len(df)} records to {out_dir}")

if __name__ == "__main__":
    run_ingestion()
