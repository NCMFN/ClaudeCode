import json
import os
import hashlib
import urllib.request
import pandas as pd
from datetime import datetime
import time

CONFIG_PATH = "src/config.json"
PINGS_URL = "https://wp-public-data.s3.amazonaws.com/pings/pings-2020-07-19-2020-07-20.csv.gz"
SERVERS_URL = "https://wp-public-data.s3.amazonaws.com/pings/servers-2020-07-19.csv"

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    urllib.request.urlretrieve(url, target_path)

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    source = config.get("rtt_data_source", "wondernetwork")

    pings_path = "data/pings.csv.gz"
    servers_path = "data/servers.csv"

    if source == "wondernetwork":
        if not os.path.exists(pings_path):
            try:
                download_file(PINGS_URL, pings_path)
            except Exception as e:
                print(f"Failed to download WonderNetwork pings: {e}")
                source = "synthetic"

        if source == "wondernetwork" and not os.path.exists(servers_path):
             try:
                download_file(SERVERS_URL, servers_path)
             except Exception as e:
                print(f"Failed to download WonderNetwork servers: {e}")
                source = "synthetic"

    if source == "kaggle" or source == "netlatency_github":
        print(f"Source {source} requested but Kaggle API/NetLatency require manual intervention or credentials in this environment. Falling back to synthetic.")
        source = "synthetic"

    if source == "synthetic":
        print("Using synthetic data fallback due to inaccessible source.")
        import numpy as np
        np.random.seed(config["random_seed"])
        dates = pd.date_range(start="2020-07-19", periods=10000, freq="1S")
        # Synthesize mean=100ms, std=50ms RTT
        rtts = np.random.normal(100, 50, 10000)
        rtts = np.clip(rtts, 10, 1000)
        time_series = pd.DataFrame({"timestamp": dates, "rtt_ms": rtts})
        rtt_csv_path = "data/rtt_time_series.csv"
        time_series.to_csv(rtt_csv_path, index=False)

        # Write dummy file to compute sha256
        time_series.to_csv(pings_path, index=False)
        sha256 = compute_sha256(pings_path)
        row_count = 10000
        date_range = "2020-07-19 synthetic"

    elif source == "wondernetwork":
        print("Loading WonderNetwork data...")
        try:
            df = pd.read_csv(pings_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')

            source_node = df['source'].iloc[0]
            dest_node = df['destination'].iloc[0]
            link_df = df[(df['source'] == source_node) & (df['destination'] == dest_node)].copy()

            time_series = df.head(10000).copy()

            rtt_csv_path = "data/rtt_time_series.csv"
            time_series[['timestamp', 'avg']].rename(columns={'avg': 'rtt_ms'}).to_csv(rtt_csv_path, index=False)

            sha256 = compute_sha256(pings_path)
            row_count = len(time_series)
            date_range = f"{time_series['timestamp'].min()} to {time_series['timestamp'].max()}"

        except Exception as e:
            print(f"Error parsing data: {e}")
            return

    manifest_df = pd.DataFrame([{
        "data_source": source,
        "row_count": row_count,
        "date_range": date_range,
        "sha256": sha256
    }])
    manifest_df.to_csv("outputs/rtt_source_manifest.csv", index=False)

    manifest = {
        "rtt_source": source,
        "row_count": row_count,
        "date_range": date_range,
        "sha256": sha256,
        "generated_at": datetime.now().isoformat()
    }
    with open("outputs/manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Data ingestion complete. Processed {row_count} rows from {source}.")

if __name__ == "__main__":
    main()
