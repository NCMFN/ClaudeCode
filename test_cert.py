import requests

def test_cert():
    # Attempting to fetch a Kaggle dataset directly is typically gated by auth,
    # but let's see what happens.
    url = "https://www.kaggle.com/datasets/nitishabharathi/cert-insider-threat"
    response = requests.get(url, stream=True, verify=False)
    print(response.status_code)
test_cert()
