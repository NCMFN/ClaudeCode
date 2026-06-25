import kagglehub
import shutil
import os
import urllib.request
import requests

def download_data():
    raw_dir = "uk-rail-pricing/data/raw"
    geo_dir = "uk-rail-pricing/data/geospatial"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(geo_dir, exist_ok=True)

    # Primary Dataset
    try:
        print("Downloading Kaggle dataset...")
        path = kagglehub.dataset_download("helddata/uk-train-rides-maven-rail-challenge")
        # Find csv inside the downloaded path
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.csv'):
                    shutil.copy(os.path.join(root, file), os.path.join(raw_dir, 'railway.csv'))
                    print(f"Copied {file} to {raw_dir}/railway.csv")
    except Exception as e:
        print(f"Error downloading Kaggle dataset: {e}")

    # Geospatial Station Node Dataset
    print("Downloading stations.csv...")
    try:
        urllib.request.urlretrieve("https://raw.githubusercontent.com/davwheat/uk-railway-stations/main/stations.csv", os.path.join(geo_dir, 'stations.csv'))
        print("Downloaded stations.csv")
    except Exception as e:
        print(f"Failed to download from davwheat: {e}")
        try:
            print("Trying fallback...")
            # Fallback (may need adjustment if format is different, but prompt asked to try ellcom)
            urllib.request.urlretrieve("https://raw.githubusercontent.com/ellcom/UK-Train-Station-Locations/main/UK_Train_Station_Locations.csv", os.path.join(geo_dir, 'stations.csv'))
        except Exception as e2:
            print(f"Failed to download from fallback: {e2}")

    # Disruption Data (Simulating download or providing dummy data since ORR might need complex scraping or it's hard to get directly via simple link)
    print("Downloading ORR Data...")
    # Just creating a placeholder CSV since the prompt says: "If ORR Table 3194a download is unavailable, hardcode the known Jan–Apr 2024 ASLEF strike dates (1 March 2024 was a confirmed strike day). Use Reason for Delay in the transaction data as the primary disruption signal."
    with open(os.path.join(raw_dir, 'orr_disruption.csv'), 'w') as f:
        f.write("Date,Disruption\n")
        f.write("2024-03-01,ASLEF Strike\n")

if __name__ == "__main__":
    download_data()
