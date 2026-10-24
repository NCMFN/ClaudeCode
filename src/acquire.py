import os
import sys
import json
import hashlib
import time
import requests
from bs4 import BeautifulSoup

from config import get_run_mode, set_run_mode, MODE_REAL, MODE_PROTOCOL_ONLY

def verify_and_get_links():
    url = "https://csr.lanl.gov/data/cyber1/"
    try:
        res = requests.get(url, verify=True, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        links = {}
        for a in soup.find_all('a'):
            href = a.get('data-suffix')
            if href:
                if 'redteam.txt.gz' in href:
                    links['redteam'] = f"https://csr.lanl.gov/data-fence{href}"
                    links['redteam_fallback'] = f"https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz"
                if 'auth.txt.gz' in href:
                    links['auth'] = f"https://csr.lanl.gov/data-fence{href}"
                    links['auth_fallback'] = f"https://lanl.ma.ic.ac.uk/data/cyber1/auth.txt.gz"
        return links
    except Exception as e:
        print(f"Failed to fetch landing page: {e}")
        return None

def download_file(url, out_path, max_retries=3):
    for attempt in range(max_retries):
        try:
            print(f"Downloading {url} to {out_path} (Attempt {attempt+1}/{max_retries})")
            with requests.get(url, stream=True, verify=True, timeout=10) as r:
                r.raise_for_status()
                with open(out_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Download error: {e}")
            time.sleep(2 ** attempt)
    return False

def hash_file(path):
    sha = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

def validate_redteam(path):
    import gzip
    count = 0
    users = set()
    pairs = set()
    min_time = float('inf')
    max_time = 0
    try:
        with gzip.open(path, 'rt') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) != 4:
                    return False, "Invalid number of fields"
                t_str, user, src, dst = parts
                try:
                    t = int(t_str)
                    if t < 1:
                        return False, "Time < 1"
                except:
                    return False, "Invalid time format"
                count += 1
                users.add(user)
                pairs.add((src, dst))
                min_time = min(min_time, t)
                max_time = max(max_time, t)

        print(f"Redteam stats: {count} events, {len(users)} users, {len(pairs)} pairs")
        print(f"Time range: {min_time} - {max_time}")

        import csv
        os.makedirs("outputs/tables", exist_ok=True)
        with open("outputs/tables/redteam_summary.csv", "w", newline='') as cf:
            writer = csv.writer(cf)
            writer.writerow(["events", "users", "pairs", "min_time", "max_time"])
            writer.writerow([count, len(users), len(pairs), min_time, max_time])

        return True, ""
    except Exception as e:
        return False, str(e)

def main():
    os.makedirs("data/lanl", exist_ok=True)
    redteam_path = "data/lanl/redteam.txt.gz"

    links = verify_and_get_links()
    if not links or 'redteam' not in links or 'auth' not in links:
        print("Could not find links on landing page. Checking for local files...")
    else:
        if not os.path.exists(redteam_path):
            success = download_file(links['redteam'], redteam_path)
            if not success:
                print("Primary download failed. Trying fallback.")
                download_file(links['redteam_fallback'], redteam_path)

    if not os.path.exists(redteam_path):
        print("No redteam file found. Switching to PROTOCOL_ONLY mode.")
        set_run_mode(MODE_PROTOCOL_ONLY, "Redteam file not found")
        return

    valid, reason = validate_redteam(redteam_path)
    if not valid:
        print(f"Redteam file invalid: {reason}. Switching to PROTOCOL_ONLY mode.")
        set_run_mode(MODE_PROTOCOL_ONLY, f"Invalid redteam: {reason}")
        return

    size = os.path.getsize(redteam_path)
    sha = hash_file(redteam_path)
    with open("data/lanl/MANIFEST.json", "w") as f:
        json.dump({"redteam.txt.gz": {"size": size, "sha256": sha}}, f)

    # Write fallback URL for auth if we need to stream it later
    with open("data/lanl/links.json", "w") as f:
        json.dump(links, f)

    set_run_mode(MODE_REAL)

if __name__ == "__main__":
    main()
