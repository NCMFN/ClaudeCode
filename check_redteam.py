import requests
import gzip
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz"
resp = requests.get(url, stream=True, verify=False)
with gzip.open(resp.raw, 'rt') as f:
    for i in range(10):
        print(f.readline().strip())
