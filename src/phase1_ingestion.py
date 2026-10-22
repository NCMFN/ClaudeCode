import pandas as pd
import requests
import gzip
import urllib3
import os
import random
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_lanl_data(max_benign=50000):
    print("Streaming LANL redteam data...")
    redteam_url = "https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz"

    malicious_events = set()
    malicious_lines = []
    try:
        response = requests.get(redteam_url, stream=True, verify=False)
        response.raise_for_status()
        with gzip.open(response.raw, 'rt') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    ts = parts[0]
                    user = parts[1]
                    comp1 = parts[2]
                    malicious_events.add(f"{ts}_{user}")
                    malicious_lines.append(parts)
    except Exception as e:
        print(f"Error fetching LANL redteam data: {e}")
        return pd.DataFrame()

    print(f"Loaded {len(malicious_events)} malicious event signatures.")

    records = []

    # Randomly assign true LANL schema events to malicious records to avoid the LogOn string artifact
    # auth_type is usually ?, Negotiate, NTLM, Kerberos, MicroSoft_Authentication_Package_v1_0
    # logon_type is usually ?, Network, Interactive, NetworkCleartext, Unlock, Batch
    valid_event_types = ["Network", "Interactive", "Batch", "Unlock", "NetworkCleartext", "?"]

    print(f"Injecting {len(malicious_lines)} true malicious events from redteam dataset (with randomized true LANL schema events)...")
    for parts in malicious_lines:
        ts = parts[0]
        user = parts[1]
        comp1 = parts[2]
        records.append({
            "timestamp": int(ts),
            "user_id": user,
            "host_id": comp1,
            "event_type": random.choice(valid_event_types),
            "modality": "auth",
            "label": "malicious"
        })

    try:
        auth_url = "https://lanl.ma.ic.ac.uk/data/cyber1/auth.txt.gz"
        response = requests.get(auth_url, stream=True, verify=False)

        benign_reservoir = []

        with gzip.open(response.raw, 'rt') as f:
            for i, line in enumerate(f):
                parts = line.strip().split(',')
                if len(parts) == 9:
                    ts, src_user, dst_user, src_comp, dst_comp, auth_type, logon_type, auth_orient, success = parts
                    event_id = f"{ts}_{src_user}"

                    if event_id not in malicious_events:
                        row = {
                            "timestamp": int(ts),
                            "user_id": src_user,
                            "host_id": src_comp,
                            "event_type": logon_type,
                            "modality": "auth",
                            "label": "benign"
                        }
                        if len(benign_reservoir) < max_benign:
                            benign_reservoir.append(row)
                        else:
                            j = random.randint(0, i)
                            if j < max_benign:
                                benign_reservoir[j] = row

                # Check 500k lines to ensure reasonable runtime in sandbox
                if i >= 500000:
                    break

        records.extend(benign_reservoir)

    except Exception as e:
        print(f"Error fetching LANL auth data: {e}")

    df = pd.DataFrame(records)
    if not df.empty:
        mal_count = (df['label'] == 'malicious').sum()
        total = len(df)
        print(f"Loaded {total} LANL records. (Malicious: {mal_count})")
        print(f"Synthetic imbalance ratio: {mal_count/total:.6f} (True LANL rate is ~0.0000007)")
    return df

def run_ingestion():
    random.seed(42)
    df = load_lanl_data()
    if df.empty:
        print("Error: No data loaded.")
        return

    df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', origin=pd.Timestamp('2015-01-01'))
    df['day'] = df['datetime'].dt.date

    out_dir = "outputs/datasets/harmonized_events"
    os.makedirs(out_dir, exist_ok=True)

    for f in os.listdir(out_dir):
        if os.path.isdir(os.path.join(out_dir, f)):
            import shutil
            shutil.rmtree(os.path.join(out_dir, f))

    df.to_parquet(out_dir, partition_cols=['day'], engine='pyarrow', index=False)
    print(f"Successfully harmonized {len(df)} records to {out_dir}")

if __name__ == "__main__":
    run_ingestion()
