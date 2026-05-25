import urllib.request
import os
url = "https://data.dtu.dk/ndownloader/articles/21511815/versions/1"
try:
    print("Trying to download DTU dataset...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        with open("data/dtu/dtu_data.zip", "wb") as f:
            f.write(response.read())
    print("Success")
except Exception as e:
    print(f"Failed: {e}")
