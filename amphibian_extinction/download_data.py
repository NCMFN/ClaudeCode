import urllib.request
import pandas as pd
import zipfile
import io
import os

os.makedirs('data', exist_ok=True)

try:
    print("Downloading AmphiBIO...")
    url = "https://ndownloader.figshare.com/files/7525348"
    urllib.request.urlretrieve(url, "data/AmphiBIO_v1.csv")
    df = pd.read_csv("data/AmphiBIO_v1.csv")
    print("AmphiBIO shape:", df.shape)
except Exception as e:
    print(e)
