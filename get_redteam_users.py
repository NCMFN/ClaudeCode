import requests, gzip
url = "https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz"
resp = requests.get(url, stream=True, verify=False)
lines = []
with gzip.open(resp.raw, 'rt') as f:
    for _ in range(50):
        lines.append(f.readline().strip())
print(lines[:10])
