import urllib.request
import pandas as pd
import zipfile
import io

try:
    url = "https://ndownloader.figshare.com/files/7525348" # AmphiBIO v1
    print("Downloading AmphiBIO...")
    urllib.request.urlretrieve(url, "AmphiBIO_v1.csv")
    df = pd.read_csv("AmphiBIO_v1.csv")
    print(df.head())
    print("Columns:", df.columns.tolist())
except Exception as e:
    print(e)
