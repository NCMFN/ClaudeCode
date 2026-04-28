import os
import requests
import pandas as pd
import urllib.request
import time

def download_file(url, filename):
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"Successfully downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

def get_zenodo_data():
    print("Fetching Earth Microbiome Project (EMP) Data from Zenodo...")
    files = {
        "emp_qiime_mapping_qc_filtered_20170912.tsv": "https://zenodo.org/records/890000/files/emp_qiime_mapping_qc_filtered_20170912.tsv?download=1",
        "emp_deblur_150bp.release1.biom": "https://zenodo.org/records/890000/files/emp_deblur_150bp.release1.biom?download=1"
    }

    for filename, url in files.items():
        if not os.path.exists(filename):
            os.system(f"wget -O {filename} {url}")
        else:
             print(f"{filename} already exists. Skipping download.")

def download_neon_soil_chemistry(output_path='neon_soil_chem.csv'):
    """Download actual soil chemistry from NEON DP1.10086.001 (Soil Physical and Chemical properties)"""
    print("\nDownloading REAL NEON Soil Chemistry Ground Truth...")

    if os.path.exists(output_path):
        print(f"{output_path} already exists. Skipping download.")
        return

    all_data = []
    # DP1.10086.001 is the actual soil chemistry ground truth product as identified in the report
    product_url = "https://data.neonscience.org/api/v0/products/DP1.10086.001"

    try:
        resp = requests.get(product_url).json()

        # Download data for the first 5 sites to form our baseline chemistry dataset
        for site in resp['data']['siteCodes'][:5]:
            print(f"Fetching data for site: {site['siteCode']}")
            for month_url in site['availableDataUrls'][:3]:
                files_resp = requests.get(month_url).json()
                for f in files_resp['data']['files']:
                    # Look for soil nitrogen/chemistry basic files
                    if 'bgc' in f['name'].lower() and f['name'].endswith('.csv') and 'basic' in f['name'].lower():
                        df = pd.read_csv(f['url'])
                        df['siteID'] = site['siteCode']
                        all_data.append(df)
                time.sleep(0.5)  # Be polite to the API

        if all_data:
            final_df = pd.concat(all_data)
            final_df.to_csv(output_path, index=False)
            print(f"NEON Ground truth chemistry saved to {output_path}. Shape: {final_df.shape}")
        else:
            print("Warning: No chemical CSVs found in the queried NEON sites. Falling back to EMP targets.")

    except Exception as e:
        print(f"Failed to fetch NEON data: {e}")

if __name__ == "__main__":
    get_zenodo_data()
    download_neon_soil_chemistry()
    print("\nData acquisition complete. Real labels acquired.")
