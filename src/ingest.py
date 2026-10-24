import os
import sys
import gzip
import csv
import json
import random
import requests
import pandas as pd
import numpy as np

from config import get_run_mode, set_run_mode, MODE_REAL, MODE_PROTOCOL_ONLY
from config import SEED, N_BENIGN_USERS, MAX_LINES, MAX_SECONDS

def load_redteam(path):
    import gzip
    redteam = set()
    redteam_users = set()
    with gzip.open(path, 'rt') as f:
        for line in f:
            parts = line.strip().split(',')
            t = int(parts[0])
            user = parts[1]
            src = parts[2]
            dst = parts[3]
            redteam.add((t, user, src, dst))
            redteam_users.add(user)
    return redteam, redteam_users

def stream_auth_users(auth_url, redteam_users):
    """ First pass: just collect distinct human users to sample benign users. """
    random.seed(SEED)
    human_users = set()

    print("Streaming auth for user collection...")
    req = requests.get(auth_url, stream=True, verify=True, timeout=10)
    req.raise_for_status()

    # Due to size, we might only read a subset to find users.
    # The requirement: "keep every user that appears in red-team, plus N_BENIGN_USERS"
    # To do this correctly, we must sample from all users, but we can't load the whole file.
    # We will sample from the first MAX_LINES to get candidate users.

    with gzip.open(req.raw, 'rt') as f:
        count = 0
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 9:
                user = parts[1]
                # exclude computer accounts ending in $ and ANONYMOUS LOGON
                if not user.endswith('$') and 'ANONYMOUS LOGON' not in user:
                    human_users.add(user)
            count += 1
            if count >= MAX_LINES:
                break

    benign_candidates = sorted(list(human_users - redteam_users))
    if len(benign_candidates) < N_BENIGN_USERS:
        sampled_benign = set(benign_candidates)
    else:
        sampled_benign = set(random.sample(benign_candidates, N_BENIGN_USERS))

    return sampled_benign

def stream_and_extract(auth_url, target_users, redteam):
    print("Streaming auth for data extraction...")
    req = requests.get(auth_url, stream=True, verify=True, timeout=10)
    req.raise_for_status()

    records = []
    redteam_matched = 0
    lines_read = 0
    malformed = 0
    max_time_reached = 0

    with gzip.open(req.raw, 'rt') as f:
        for line in f:
            lines_read += 1
            parts = line.strip().split(',')
            if len(parts) != 9:
                malformed += 1
                continue

            t_str, src_user, dst_user, src_comp, dst_comp, auth_type, logon_type, orientation, success = parts
            try:
                t = int(t_str)
            except:
                malformed += 1
                continue

            max_time_reached = max(max_time_reached, t)

            if src_user in target_users:
                # check if positive
                is_positive = (t, src_user, src_comp, dst_comp) in redteam
                if is_positive:
                    redteam_matched += 1

                records.append({
                    'time': t,
                    'user': src_user,
                    'src_comp': src_comp,
                    'dst_comp': dst_comp,
                    'auth_type': auth_type,
                    'logon_type': logon_type,
                    'orientation': orientation,
                    'success': success,
                    'label': 1 if is_positive else 0
                })

            if lines_read >= MAX_LINES:
                break

    return records, lines_read, malformed, max_time_reached, redteam_matched

def ingest():
    if get_run_mode() == MODE_PROTOCOL_ONLY:
        print("PROTOCOL_ONLY mode: skipping ingest.")
        return

    links_path = "data/lanl/links.json"
    if not os.path.exists(links_path):
        print("No links.json found. Cannot ingest auth stream.")
        set_run_mode(MODE_PROTOCOL_ONLY, "auth link not found")
        return

    with open(links_path, 'r') as f:
        links = json.load(f)

    auth_url = links.get('auth')
    # Use fallback because main is 404
    auth_url = links.get('auth_fallback', auth_url)

    redteam, redteam_users = load_redteam("data/lanl/redteam.txt.gz")

    sampled_benign = stream_auth_users(auth_url, redteam_users)
    target_users = redteam_users.union(sampled_benign)
    print(f"Target users: {len(target_users)} ({len(redteam_users)} redteam, {len(sampled_benign)} benign)")

    records, lines_read, malformed, max_time_reached, redteam_matched = stream_and_extract(auth_url, target_users, redteam)

    redteam_unmatched = len(redteam) - redteam_matched
    print(f"Ingest stats: read {lines_read}, malformed {malformed}, max_time {max_time_reached}")
    print(f"Redteam matched: {redteam_matched}, unmatched: {redteam_unmatched}")

    # If evaluation window not fully reached within budget, set mode PROTOCOL_ONLY
    redteam_max_time = max(t for t, u, s, d in redteam)
    if max_time_reached < redteam_max_time:
        print(f"WARNING: Max time reached ({max_time_reached}) is less than redteam max time ({redteam_max_time}). Evaluation window truncated!")
        set_run_mode(MODE_PROTOCOL_ONLY, "Evaluation window not fully reached within max_lines budget")
        return

    df = pd.DataFrame(records)

    # Calculate day_index and second_of_day
    df['day_index'] = (df['time'] - 1) // 86400
    df['second_of_day'] = (df['time'] - 1) % 86400

    os.makedirs("outputs/datasets", exist_ok=True)
    df.to_parquet("outputs/datasets/ingested.parquet", index=False)

    os.makedirs("outputs/tables", exist_ok=True)
    with open("outputs/tables/ingest_report.csv", "w", newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["lines_read", "malformed", "max_time_reached", "redteam_matched", "redteam_unmatched"])
        writer.writerow([lines_read, malformed, max_time_reached, redteam_matched, redteam_unmatched])

    with open("outputs/tables/redteam_unmatched.csv", "w", newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["time", "user", "src", "dst"])
        for t, u, s, d in redteam:
            # We don't strictly track which individual ones matched in memory for this print unless we do a set diff
            pass

    # Properly track unmatched
    matched_set = set((r['time'], r['user'], r['src_comp'], r['dst_comp']) for r in records if r['label'] == 1)
    unmatched = redteam - matched_set
    with open("outputs/tables/redteam_unmatched.csv", "w", newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["time", "user", "src", "dst"])
        for t, u, s, d in unmatched:
            writer.writerow([t, u, s, d])

if __name__ == "__main__":
    ingest()
