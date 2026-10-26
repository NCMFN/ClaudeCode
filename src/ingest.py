import os
import requests
import gzip
import logging
import pandas as pd
import pyarrow.csv as pv
import pyarrow.parquet as pq
import pyarrow as pa
from typing import Optional, Dict, Set, Tuple
import hashlib
import csv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AUTH_URL = "https://csr.lanl.gov/data/cyber1/auth.txt.gz"
REDTEAM_URL = "https://csr.lanl.gov/data/cyber1/redteam.txt.gz"

def download_file(url: str, output_path: str, expected_size: Optional[int] = None) -> bool:
    headers = {}
    if os.path.exists(output_path):
        current_size = os.path.getsize(output_path)
        if expected_size and current_size == expected_size:
            logger.info(f"File {output_path} already downloaded.")
            return True
        headers['Range'] = f'bytes={current_size}-'
        mode = 'ab'
        logger.info(f"Resuming download of {output_path} from byte {current_size}...")
    else:
        mode = 'wb'
        logger.info(f"Starting download of {output_path}...")

    try:
        response = requests.get(url, headers=headers, stream=True, verify=True, timeout=60)

        if response.status_code == 416:
            logger.info(f"File {output_path} might be fully downloaded already.")
            return True

        if response.status_code not in (200, 206):
            logger.error(f"Download failed with status {response.status_code}: {response.text}")
            return False

        with open(output_path, mode) as f:
            for chunk in response.iter_content(chunk_size=8192 * 1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"Download error: {e}")
        return False

def get_file_sha256(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def normalize_user(u: str) -> str:
    if not isinstance(u, str):
        return ""
    return u.strip().lower()

def load_redteam_events(filepath: str) -> Set[tuple]:
    redteam_set = set()
    if not os.path.exists(filepath):
        return redteam_set
    try:
        with gzip.open(filepath, 'rt') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    redteam_set.add((int(parts[0]), normalize_user(parts[1]), parts[2].strip(), parts[3].strip()))
    except Exception as e:
         logger.error(f"Error reading redteam file: {e}")
    return redteam_set

def ingest_auth_data(input_gz_path: str, redteam_set: Set[tuple], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    column_names = [
        'time', 'src_user', 'dst_user', 'src_comp', 'dst_comp',
        'auth_type', 'logon_type', 'auth_orientation', 'success'
    ]

    convert_options = pv.ConvertOptions(
        column_types={
            'time': pa.int64(), 'src_user': pa.string(), 'dst_user': pa.string(),
            'src_comp': pa.string(), 'dst_comp': pa.string(), 'auth_type': pa.string(),
            'logon_type': pa.string(), 'auth_orientation': pa.string(), 'success': pa.string(),
        }
    )
    read_options = pv.ReadOptions(column_names=column_names, block_size=256 * 1024 * 1024)
    parse_options = pv.ParseOptions(delimiter=',')

    total_rows = 0
    malicious_rows = 0

    matched_rt = set()
    rt_by_time = {}
    for ev in redteam_set:
        rt_by_time.setdefault(ev[0], []).append(ev)

    rt_diagnostic_reasons = {}

    try:
         with gzip.open(input_gz_path, 'rb') as f:
             reader = pv.open_csv(f, read_options=read_options, parse_options=parse_options, convert_options=convert_options)
             chunk_idx = 0
             for batch in reader:
                 df = batch.to_pandas()
                 df['is_malicious'] = 0

                 df['src_user_norm'] = df['src_user'].apply(normalize_user)
                 df['src_comp_strip'] = df['src_comp'].str.strip()
                 df['dst_comp_strip'] = df['dst_comp'].str.strip()

                 keys = pd.Series(zip(df['time'], df['src_user_norm'], df['src_comp_strip'], df['dst_comp_strip']))
                 mask = keys.isin(redteam_set)
                 df.loc[mask, 'is_malicious'] = 1

                 matched_rt.update(keys[mask].tolist())
                 malicious_rows += mask.sum()

                 chunk_times = set(df['time'].unique())
                 times_to_check = set(rt_by_time.keys()).intersection(chunk_times)

                 for t in times_to_check:
                     chunk_t_df = df[df['time'] == t]
                     for rt_ev in rt_by_time[t]:
                         if rt_ev not in matched_rt:
                             users_at_t = set(chunk_t_df['src_user_norm'])
                             if rt_ev[1] not in users_at_t:
                                 rt_diagnostic_reasons[rt_ev] = 'time_match_user_mismatch'
                             else:
                                 rt_diagnostic_reasons[rt_ev] = 'time_user_match_computer_mismatch'

                 df['day'] = df['time'] // 86400

                 df = df.drop(columns=['src_user_norm', 'src_comp_strip', 'dst_comp_strip'])

                 for day, group in df.groupby('day'):
                     day_dir = os.path.join(output_dir, f'day={day:02d}')
                     os.makedirs(day_dir, exist_ok=True)
                     chunk_file = os.path.join(day_dir, f'chunk_{chunk_idx:04d}.parquet')
                     group.to_parquet(chunk_file, index=False)

                 total_rows += len(df)
                 chunk_idx += 1
                 logger.info(f"Processed {total_rows} rows...")

                 if os.environ.get('PARTIAL_RUN') == '1' and total_rows > 1000000:
                     break

    except Exception as e:
         logger.error(f"Error processing auth file: {e}")

    unmatched_reasons = {}
    for ev in redteam_set:
        if ev not in matched_rt:
            if ev in rt_diagnostic_reasons:
                unmatched_reasons[ev] = rt_diagnostic_reasons[ev]
            else:
                unmatched_reasons[ev] = 'no_auth_at_timestamp'

    if os.environ.get('PARTIAL_RUN') == '1':
        for ev in redteam_set:
            if ev not in matched_rt and unmatched_reasons.get(ev) == 'no_auth_at_timestamp':
                unmatched_reasons[ev] = 'outside_file_coverage'

    os.makedirs('outputs/tables', exist_ok=True)
    with open('outputs/tables/redteam_unmatched.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'src_user', 'src_comp', 'dst_comp', 'reason'])
        for ev, reason in unmatched_reasons.items():
            writer.writerow([ev[0], ev[1], ev[2], ev[3], reason])

    return total_rows, malicious_rows, unmatched_reasons
