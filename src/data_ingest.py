import os, json, urllib.request, hashlib, yaml, pandas as pd
from datetime import datetime
with open("config.yaml", "r") as f: config = yaml.safe_load(f)
PINGS_URL = "https://wp-public-data.s3.amazonaws.com/pings/pings-2020-07-19-2020-07-20.csv.gz"
SERVERS_URL = "https://wp-public-data.s3.amazonaws.com/pings/servers-2020-07-19.csv"
DATA_DIR = "data"
def download_file(url, local_path):
    if not os.path.exists(local_path): urllib.request.urlretrieve(url, local_path)
    return local_path
def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for b in iter(lambda: f.read(4096), b""): h.update(b)
    return h.hexdigest()
def ingest_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    pings_path = download_file(PINGS_URL, os.path.join(DATA_DIR, "pings.csv.gz"))
    servers_path = download_file(SERVERS_URL, os.path.join(DATA_DIR, "servers.csv"))
    sha256 = get_sha256(pings_path)
    df_iter = pd.read_csv(pings_path, compression='gzip', chunksize=500000, names=['source', 'destination', 'timestamp', 'min', 'avg', 'max', 'mdev'], header=None)
    df_chunk = next(df_iter).dropna()
    df_chunk['avg'] = pd.to_numeric(df_chunk['avg'], errors='coerce')
    df_chunk = df_chunk.dropna()
    best_pair = df_chunk.groupby(['source', 'destination']).size().reset_index(name='count').sort_values('count', ascending=False).iloc[0]
    s_id, d_id = best_pair['source'], best_pair['destination']
    rtt_series, timestamps = [], []
    def proc(chunk):
        c = chunk[(chunk['source'] == s_id) & (chunk['destination'] == d_id)]
        if not c.empty:
            c['avg'] = pd.to_numeric(c['avg'], errors='coerce')
            c = c[c['avg'] > 0].sort_values('timestamp')
            rtt_series.extend(c['avg'].tolist())
            timestamps.extend(c['timestamp'].tolist())
    proc(df_chunk)
    for chunk in df_iter:
        proc(chunk)
        if len(rtt_series) > 5000: break
    df_path = pd.DataFrame({'t': timestamps, 'r': rtt_series}).sort_values('t')
    rtt_s = df_path['r'].tolist()
    while len(rtt_s) < 1000: rtt_s.extend(rtt_s)
    rtt_s = rtt_s[:2000]
    start_time, end_time = df_path['t'].min(), df_path['t'].max()
    try: start_date, end_date = datetime.utcfromtimestamp(pd.to_numeric(start_time)).isoformat(), datetime.utcfromtimestamp(pd.to_numeric(end_time)).isoformat()
    except: start_date, end_date = str(start_time), str(end_time)
    with open("outputs/manifest.json", "w") as f: json.dump({"source_url": PINGS_URL, "row_count_used": len(rtt_s), "date_range": [start_date, end_date], "sha256": sha256, "source_node": str(s_id), "dest_node": str(d_id)}, f, indent=4)
    pd.DataFrame({'rtt_ms': rtt_s}).to_csv("data/rtt_time_series.csv", index=False)
if __name__ == "__main__": ingest_data()
