import urllib.request
import os

url = "https://media.githubusercontent.com/media/dfitzgerald0/cert-insider-threat/master/data/r6.2/logon.csv"
try:
    print("Trying to download CERT from github...")
    urllib.request.urlretrieve(url, "logon.csv")
    print("Success")
except Exception as e:
    print(e)
