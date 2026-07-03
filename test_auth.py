import requests
import gzip
import urllib3
import itertools

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_stream():
    url = "https://lanl.ma.ic.ac.uk/data/cyber1/auth.txt.gz"
    response = requests.get(url, stream=True, verify=False)
    print("auth status:", response.status_code)

    with gzip.open(response.raw, 'rt') as f:
        for i, line in enumerate(f):
            print(line.strip())
            if i >= 5:
                break

test_stream()
