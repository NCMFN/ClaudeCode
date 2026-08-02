import os
import json
import gzip
import hashlib
import pandas as pd
import requests
import yaml
from pathlib import Path

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

def download_file(url, cache_path):
    if not cache_path.exists():
        print(f"Downloading {url} to {cache_path}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(cache_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"Using cached file {cache_path}")

def compute_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def ingest_data():
    config = load_config()
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    if config["rtt_data_source"] == "wondernetwork":
        pings_url = "https://wp-public-data.s3.amazonaws.com/pings/pings-2020-07-19-2020-07-20.csv.gz"
        servers_url = "https://wp-public-data.s3.amazonaws.com/pings/servers-2020-07-19.csv"

        pings_cache = cache_dir / "pings.csv.gz"
        servers_cache = cache_dir / "servers.csv"

        download_file(pings_url, pings_cache)
        download_file(servers_url, servers_cache)

        print("Loading data into pandas...")
        df_pings = pd.read_csv(pings_cache, compression='gzip')

        df_pings['timestamp'] = pd.to_datetime(df_pings['timestamp'])
        df_pings = df_pings.sort_values('timestamp')

        df_series = df_pings[['timestamp', 'avg']].dropna()
        df_series = df_series.sort_values('timestamp').reset_index(drop=True)

        if len(df_series) > 100000:
            df_series = df_series.iloc[:100000]

        rtt_series = df_series['avg'].values

        manifest = {
            "source": "wondernetwork",
            "pings_url": pings_url,
            "servers_url": servers_url,
            "row_count": len(df_series),
            "date_range": [str(df_series['timestamp'].min()), str(df_series['timestamp'].max())],
            "pings_sha256": compute_sha256(pings_cache),
            "servers_sha256": compute_sha256(servers_cache)
        }

    else:
        raise NotImplementedError("Only wondernetwork is implemented for now.")

    with open(outputs_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)

    print(f"Data ingested. {len(rtt_series)} RTT points extracted.")
    return rtt_series

if __name__ == "__main__":
    rtt = ingest_data()
