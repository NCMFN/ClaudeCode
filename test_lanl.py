import requests
import gzip

try:
    response = requests.get("https://lanl.ma.ic.ac.uk/data/cyber1/redteam.txt.gz", stream=True, verify=False, timeout=10)
    print("Status code:", response.status_code)
except Exception as e:
    print("Error:", e)
