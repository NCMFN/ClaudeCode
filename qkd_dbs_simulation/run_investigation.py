import requests

def test_urls():
    urls = [
        "https://wp-public-data.s3.amazonaws.com/pings/pings-2020-07-19-2020-07-20.csv.gz",
        "https://wp-public-data.s3.amazonaws.com/pings/servers-2020-07-19.csv"
    ]
    for url in urls:
        r = requests.head(url)
        print(f"{url}: {r.status_code}")

if __name__ == "__main__":
    test_urls()
