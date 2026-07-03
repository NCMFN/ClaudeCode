import requests
url = "https://www.impactcybertrust.org/dataset_view?idDataset=1297"
response = requests.get(url, verify=False)
print(response.status_code)
