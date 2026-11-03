import os
import sys
import subprocess
import shutil
import requests
import json
from datetime import datetime
import yaml

def load_config():
    with open("config/protocol.yaml") as f:
        return yaml.safe_load(f)

def check_disk_space(path=".", min_gb=45):
    total, used, free = shutil.disk_usage(path)
    free_gb = free / (1024**3)
    return free_gb >= min_gb, free_gb

def get_redacted_url(url):
    if "csr.lanl.gov/data-fence" in url:
        parts = url.split('/')
        if len(parts) > 4:
            parts[4] = "<REDACTED>"
            return "/".join(parts)
    return url

def check_url(url):
    try:
        head = requests.head(url, timeout=10)
        return head.status_code, head.url, head.headers.get('Content-Length')
    except Exception:
        try:
            head = requests.get(url, headers={'Range': 'bytes=0-0'}, timeout=10)
            return head.status_code, head.url, head.headers.get('Content-Length')
        except Exception:
            return None, None, None

def check_gzip(filepath):
    res = subprocess.run(["gzip", "-t", filepath], capture_output=True)
    return res.returncode == 0

def write_status(msg):
    with open("STATUS.md", "w") as f:
        f.write(msg + "\n")

def get_hash(filepath):
    import hashlib
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def download():
    config = load_config()
    local_dir = os.environ.get("LANL_DATA_DIR", config['data']['local_dir'])
    os.makedirs(local_dir, exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    with open(".gitignore", "a") as f:
        f.write("\ndata/\n.env\n*.part\n")

    if os.path.exists(f"{local_dir}/auth.txt.gz") and os.path.exists(f"{local_dir}/redteam.txt.gz"):
        if check_gzip(f"{local_dir}/auth.txt.gz") and check_gzip(f"{local_dir}/redteam.txt.gz"):
            print("Using local files.")
            with open("outputs/run_state.json", "w") as f:
                json.dump({"stage": "ingest"}, f)
            return

    auth_url = os.environ.get("LANL_AUTH_URL")
    redteam_url = os.environ.get("LANL_REDTEAM_URL")

    try:
        from google.colab import userdata
        if not auth_url: auth_url = userdata.get('LANL_AUTH_URL')
        if not redteam_url: redteam_url = userdata.get('LANL_REDTEAM_URL')
    except ImportError:
        pass

    if not auth_url or not redteam_url:
        print("PROPOSED METHODOLOGY: URLs not set.")
        write_status("PROPOSED METHODOLOGY: no validation performed. Links missing. See RESUME.md")
        sys.exit(0)

    ok, free = check_disk_space(min_gb=config['data']['minimum_disk_gb'])
    if not ok:
        write_status(f"PROPOSED METHODOLOGY: no validation performed. Disk shortfall: only {free:.1f}GB free.")
        sys.exit(0)

    meta = {}
    for url, name in [(auth_url, "auth"), (redteam_url, "redteam")]:
        status, final_url, clen = check_url(url)
        if status in (401, 403, 404, 410):
            write_status(f"PROPOSED METHODOLOGY: download links expired or denied (HTTP {status})")
            sys.exit(0)
        if status is None:
            write_status(f"PROPOSED METHODOLOGY: reachability failed for {name}")
            sys.exit(0)
        meta[name] = {
            "status": status,
            "final_url_redacted": get_redacted_url(final_url) if final_url else None,
            "content_length": clen,
            "url_redacted": get_redacted_url(url)
        }

    with open("src/curl_env.sh", "w") as f:
        f.write('#!/bin/bash\n')
        # Do not use eval, use indirection
        f.write('URL="${!1}"\n')
        f.write('OUT=$2\n')
        f.write('curl -L --fail --silent --show-error -C - --retry 5 --retry-delay 10 -o "$OUT" "$URL"\n')
    os.chmod("src/curl_env.sh", 0o755)

    import time
    def run_download_env(env_var_name, out_part, final_name, exp_size):
        if os.path.exists(final_name): return True
        proc = subprocess.Popen(["./src/curl_env.sh", env_var_name, out_part])
        start = time.time()
        while proc.poll() is None:
            time.sleep(10)
            if time.time() - start > 550:
                print("Download approaching 10 min. Terminating to resume later.")
                proc.terminate()
                with open("outputs/run_state.json", "w") as f:
                    json.dump({"stage": "download_incomplete"}, f)
                sys.exit(0)

        if proc.returncode == 0:
            sz = os.path.getsize(out_part)
            if exp_size and abs(sz - exp_size) > exp_size * 0.1: # simple size sanity
                write_status("PROPOSED METHODOLOGY: size mismatch")
                sys.exit(0)
            os.rename(out_part, final_name)
            return True
        else:
            sz = os.path.getsize(out_part) if os.path.exists(out_part) else 0
            write_status(f"PROPOSED METHODOLOGY: download failed. Byte offset reached: {sz}")
            sys.exit(0)

    # Assuming auth is ~7.2GB, redteam ~4.8KB
    run_download_env("LANL_AUTH_URL", f"{local_dir}/auth.txt.gz.part", f"{local_dir}/auth.txt.gz", 7000000000)
    run_download_env("LANL_REDTEAM_URL", f"{local_dir}/redteam.txt.gz.part", f"{local_dir}/redteam.txt.gz", 4800)

    if not check_gzip(f"{local_dir}/auth.txt.gz") or not check_gzip(f"{local_dir}/redteam.txt.gz"):
        write_status("PROPOSED METHODOLOGY: gzip validation failed.")
        sys.exit(0)

    print("Download completed successfully.")
    with open("outputs/provenance.json", "w") as f:
        json.dump({
            "status": "PARTIAL", # Never write COMPLETED from download
            "retrieval_date": datetime.utcnow().isoformat(),
            "acquisition_mode": "signed_link_download",
            "auth": meta["auth"],
            "redteam": meta["redteam"],
            "auth_sha256": get_hash(f"{local_dir}/auth.txt.gz"),
            "redteam_sha256": get_hash(f"{local_dir}/redteam.txt.gz"),
            "commit": subprocess.getoutput("git rev-parse HEAD")
        }, f)

    with open("outputs/run_state.json", "w") as f:
        json.dump({"stage": "ingest"}, f)

if __name__ == "__main__":
    download()
