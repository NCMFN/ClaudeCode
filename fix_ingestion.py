with open("src/phase1_ingestion.py", "w") as f:
    f.write("""import pandas as pd
import requests
import gzip
import urllib3
import os

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
                    time = parts[0]
                    user = parts[1]
                    comp1 = parts[2]
                    comp2 = parts[3] if len(parts)>3 else ""
                    malicious_events.add(f"{time}_{user}")
                    malicious_lines.append(parts)
    except Exception as e:
        print(f"Error fetching LANL redteam data: {e}")
        return pd.DataFrame()

    print(f"Loaded {len(malicious_events)} malicious event signatures.")

    records = []

    print(f"Injecting {len(malicious_lines)} true malicious events from redteam dataset...")
    for parts in malicious_lines:
        time = parts[0]
        user = parts[1]
        comp1 = parts[2]
        comp2 = parts[3] if len(parts)>3 else "?"
        records.append({
            "timestamp": int(time),
            "user_id": user,
            "host_id": comp1,
            "event_type": "LogOn",
            "modality": "auth",
            "label": "malicious"
        })

    try:
        auth_url = "https://lanl.ma.ic.ac.uk/data/cyber1/auth.txt.gz"
        response = requests.get(auth_url, stream=True, verify=False)
        benign_count = 0

        with gzip.open(response.raw, 'rt') as f:
            for i, line in enumerate(f):
                parts = line.strip().split(',')
                if len(parts) == 9:
                    time, src_user, dst_user, src_comp, dst_comp, auth_type, logon_type, auth_orient, success = parts
                    event_id = f"{time}_{src_user}"
                    label = "malicious" if event_id in malicious_events else "benign"

                    if label == "benign" and benign_count < max_benign:
                        benign_count += 1
                        records.append({
                            "timestamp": int(time),
                            "user_id": src_user,
                            "host_id": src_comp,
                            "event_type": logon_type,
                            "modality": "auth",
                            "label": label
                        })

                if benign_count >= max_benign:
                    break

    except Exception as e:
        print(f"Error fetching LANL auth data: {e}")

    df = pd.DataFrame(records)
    if not df.empty:
        print(f"Loaded {len(df)} LANL records. (Malicious: {(df['label'] == 'malicious').sum()})")
    return df

def run_ingestion():
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
""")
