import os
import sys
import gzip
import json
import yaml
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
from collections import defaultdict

def load_config():
    with open("config/protocol.yaml") as f:
        return yaml.safe_load(f)

def update_provenance(key, value):
    if not os.path.exists("outputs/provenance.json"):
        return
    with open("outputs/provenance.json", "r") as f:
        p = json.load(f)
    p[key] = value
    with open("outputs/provenance.json", "w") as f:
        json.dump(p, f, indent=2)

def ingest(partial_days=None):
    config = load_config()
    local_dir = os.environ.get("LANL_DATA_DIR", config['data']['local_dir'])
    auth_file = f"{local_dir}/auth.txt.gz"
    red_file = f"{local_dir}/redteam.txt.gz"

    if not os.path.exists(auth_file) or not os.path.exists(red_file):
        print("Data files not found. Run --download first.")
        sys.exit(1)

    print("Loading redteam data...")
    redteam_by_time = defaultdict(list)
    red_count = 0
    with gzip.open(red_file, "rt") as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) != 4:
                sys.exit(1)
            t, user, src, dst = parts
            t = int(t)
            redteam_by_time[t].append({"user": user, "src": src, "dst": dst})
            red_count += 1

    print("Streaming auth data...")
    auth_count = 0
    matched_redteam = 0
    unmatched_reasons = defaultdict(int)

    out_dir = "outputs/parquet/auth"
    os.makedirs(out_dir, exist_ok=True)

    schema = pa.schema([
        ('time', pa.int64()),
        ('src_user', pa.string()),
        ('dst_user', pa.string()),
        ('src_comp', pa.string()),
        ('dst_comp', pa.string()),
        ('auth_type', pa.string()),
        ('logon_type', pa.string()),
        ('auth_orientation', pa.string()),
        ('success', pa.string()),
        ('is_redteam', pa.bool_()),
        ('day', pa.int32())
    ])

    writers = {}
    batch = defaultdict(list)

    def flush_batch(day):
        if not batch[day]: return
        df = pd.DataFrame(batch[day], columns=[f.name for f in schema])
        table = pa.Table.from_pandas(df, schema=schema)
        if day not in writers:
            writers[day] = pq.ParquetWriter(f"{out_dir}/day={day}.parquet", schema)
        writers[day].write_table(table)
        batch[day] = []

    last_time = -1
    matched_redteam_set = set()
    auth_times = set()

    try:
        with gzip.open(auth_file, "rt") as f:
            for line in f:
                parts = line.strip().split(',')
                t = int(parts[0])
                if t < last_time:
                    sys.exit(1)
                last_time = t
                auth_times.add(t)

                src_user = parts[1]
                dst_user = parts[2]
                src_comp = parts[3]
                dst_comp = parts[4]

                day = (t - 1) // 86400
                if partial_days and day > partial_days[1]:
                    break

                is_redteam = False
                if t in redteam_by_time:
                    candidates = redteam_by_time[t]
                    for cand in candidates:
                        if cand['user'] == src_user and cand['src'] == src_comp and cand['dst'] == dst_comp:
                            is_redteam = True
                            matched_redteam_set.add((t, cand['user'], cand['src'], cand['dst']))
                            break

                if is_redteam: matched_redteam += 1
                batch[day].append((t, src_user, dst_user, src_comp, dst_comp, parts[5], parts[6], parts[7], parts[8], is_redteam, day))
                auth_count += 1

                if auth_count % 1000000 == 0:
                    for d in list(batch.keys()):
                        flush_batch(d)

        for d in list(batch.keys()):
            flush_batch(d)
        for w in writers.values():
            w.close()

    except Exception as e:
        print(f"Error during ingestion: {e}")
        sys.exit(1)

    os.makedirs("outputs/tables", exist_ok=True)
    unmatched_df_data = []

    for t, candidates in redteam_by_time.items():
        for cand in candidates:
            key = (t, cand['user'], cand['src'], cand['dst'])
            if key not in matched_redteam_set:
                reason = "multiple_candidates"
                if t > last_time:
                    reason = "outside_file_coverage"
                elif t not in auth_times:
                    reason = "no_auth_at_timestamp"
                else:
                    # we don't have enough granularity to check user match vs computer mismatch without keeping all rows,
                    # but we can assume time_match_user_mismatch for simplicity if time exists.
                    reason = "time_match_user_mismatch"

                unmatched_df_data.append((*key, reason))
                unmatched_reasons[reason] += 1

    unmatched_df = pd.DataFrame(unmatched_df_data, columns=["time", "user", "src", "dst", "reason"])
    unmatched_df.to_csv("outputs/tables/redteam_unmatched.csv", index=False)

    update_provenance("auth_lines", auth_count)
    update_provenance("matched_redteam", matched_redteam)
    update_provenance("unmatched_reasons", dict(unmatched_reasons))

    with open("outputs/run_state.json", "w") as f:
        json.dump({"stage": "sampling"}, f)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=str)
    args = parser.parse_args()
    partial = None
    if args.days:
        s, e = args.days.split("-")
        partial = (int(s), int(e))
    ingest(partial)
