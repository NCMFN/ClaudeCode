import requests
import zipfile
import io
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def download_data():
    print(f"Downloading dataset from {config.UCI_URL} ...")
    try:
        response = requests.get(config.UCI_URL, timeout=60)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(config.RAW_DATA_DIR)

        print("Dataset extracted successfully to data/raw/")

        # Locate the space-delimited data file
        for root, dirs, files in os.walk(config.RAW_DATA_DIR):
            for file in files:
                if file == "data.txt" and "__MACOSX" not in root:
                    filepath = os.path.join(root, file)
                    print(f"File path found: {filepath}")

                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                        print(f"Number of rows: {len(lines)}")
                        if lines:
                            cols = len(lines[0].strip().split())
                            print(f"Number of columns: {cols}")
                            print("First 3 rows:")
                            for line in lines[:3]:
                                print(line.strip())
                    return filepath

        print("Error: Could not find data.txt in extracted files.")

    except Exception as e:
        print(f"Download failed: {e}")
        print("Manual download:")
        print("  1. Visit: https://archive.ics.uci.edu/dataset/316/condition+based+maintenance+of+naval+propulsion+plants")
        print("  2. Click \"Download\" and extract the ZIP")
        print("  3. Place the extracted files in: data/raw/")
        print("Alternative mirror: https://www.kaggle.com/datasets/elikplim/maintenance-of-naval-propulsion-plants")

if __name__ == "__main__":
    download_data()
