import requests
import gzip
import urllib3
urllib3.disable_warnings()

print("Trying mirror without timeout...")
try:
    url = "https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz"
    resp = requests.get(url, stream=True, verify=False)
    lines = []
    with gzip.open(resp.raw, 'rt') as f:
        for _ in range(10):
            lines.append(f.readline().strip())
    print("Success without timeout")
except Exception as e:
    print(f"Failed: {e}")
