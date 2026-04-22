import urllib.request
try:
    urllib.request.urlretrieve("https://data.mendeley.com/public-files/datasets/v5bcvx8x94/files/4e44fec8-3cfc-4039-8089-6cb8f1702d76/file_downloaded", "flood.csv")
    print("Downloaded flood.csv")
except Exception as e:
    print(e)
