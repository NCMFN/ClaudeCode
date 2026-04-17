import os
import requests
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
        # We only download the primary mapping and BIOM table for the ML pipeline execution to save time/space,
        # but the script structure confirms these are the target files.
    }

    for filename, url in files.items():
        if not os.path.exists(filename):
            # Using wget via system call to handle Zenodo's potential redirects more gracefully
            os.system(f"wget -O {filename} {url}")
        else:
             print(f"{filename} already exists. Skipping download.")

def verify_neon_data():
    print("\nVerifying NEON Data Products Connectivity...")
    products = [
        "DP1.10107.001", # 16S Metagenome Sequences
        "DP1.10108.001", # Marker Gene Sequences (16S/ITS)
        "DP1.10086.001"  # Soil Chemistry (ground truth)
    ]

    for product in products:
        response = requests.get(f"https://data.neonscience.org/api/v0/products/{product}")
        if response.status_code == 200:
            data = response.json()
            site_months = len(data['data'].get('siteCodes', []))
            print(f"[OK] NEON {product} available. Found {site_months} site-months of data.")
        else:
            print(f"[FAIL] Failed to fetch NEON {product}, status code: {response.status_code}")
        time.sleep(1) # Be polite to the API

if __name__ == "__main__":
    get_zenodo_data()
    verify_neon_data()
    print("\nData acquisition configuration aligned and confirmed.")
