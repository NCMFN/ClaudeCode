import requests
import gzip
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_stream():
    url = "https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz"
    response = requests.get(url, stream=True, verify=False)
    print(response.status_code)

    with gzip.open(response.raw, 'rt') as f:
        for i, line in enumerate(f):
            print(line.strip())
            if i >= 5:
                break

test_stream()
