import urllib.request
import zipfile
import io
import pandas as pd
import os

url = 'https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NHIS/2022/adult22csv.zip'
print('Downloading full NHIS dataset...')
response = urllib.request.urlopen(url)
with zipfile.ZipFile(io.BytesIO(response.read())) as z:
    with z.open('adult22.csv') as f:
        df = pd.read_csv(f)
        df.to_csv('heart_mind_cvd/data/nhis_raw/adult22.csv', index=False)
        print('Saved to heart_mind_cvd/data/nhis_raw/adult22.csv')
