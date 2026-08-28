import kagglehub
import shutil
import os

try:
    path = kagglehub.dataset_download("anikannal/solar-power-generation-data")
    print(f"Downloaded to {path}")
    for file in os.listdir(path):
        shutil.copy(os.path.join(path, file), "data/raw/")
    print("Files copied to data/raw/")
except Exception as e:
    print(f"Failed to download: {e}")
