import gzip
import os
import hashlib
import pandas as pd
import json

def main():
    filepath = "redteam.txt.gz"

    with open(filepath, "rb") as f:
        data = f.read()

    size_bytes = len(data)
    sha256 = hashlib.sha256(data).hexdigest()

    try:
        with gzip.open(filepath, 'rt') as f:
            lines = f.readlines()

        line_count = len(lines)

        all_match_format = True
        timestamps = []
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) != 4:
                all_match_format = False
                break

            try:
                ts = int(parts[0])
                timestamps.append(ts)
            except ValueError:
                all_match_format = False
                break

            user_domain = parts[1]
            if '@' not in user_domain:
                all_match_format = False
                break

        time_min, time_max = min(timestamps), max(timestamps)
        time_valid = (1 <= time_min) and (time_max <= 5011199)

        status = "PASSED" if (line_count == 749 and all_match_format and time_valid) else "FAILED"

    except Exception as e:
        status = f"FAILED: {str(e)}"
        line_count = 0
        time_min, time_max = None, None

    df = pd.DataFrame([{
        "filename": "redteam.txt.gz",
        "status": status,
        "size_bytes": size_bytes,
        "sha256": sha256,
        "line_count": line_count,
        "time_min": time_min,
        "time_max": time_max
    }])

    df.to_csv("outputs/tables/redteam_authentication.csv", index=False)

    provenance = {
        "redteam.txt.gz": {
            "host": "https://csr.lanl.gov/",
            "size_bytes": size_bytes,
            "sha256": sha256,
            "authenticated": status == "PASSED"
        },
        "auth.txt.gz": {
            "host": "https://csr.lanl.gov/",
            "status": "FAILED",
            "reason": "File is 7626505158 bytes, stream could not complete within sandbox time budget. The evaluation is deferred to a local run.",
            "bytes_downloaded": "partial (deleted)"
        }
    }

    with open("data_provenance.json", "w") as f:
        json.dump(provenance, f, indent=2)

    framing_numbers = {
        "redteam_event_count": line_count,
        "redteam_time_min": time_min,
        "redteam_time_max": time_max
    }

    os.makedirs("paper", exist_ok=True)
    with open("paper/framing_numbers.json", "w") as f:
        json.dump(framing_numbers, f, indent=2)

if __name__ == "__main__":
    main()
