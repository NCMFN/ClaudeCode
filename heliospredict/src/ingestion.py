import kagglehub
import requests
import pandas as pd
import numpy as np
import os
import shutil
from pathlib import Path

def download_kaggle_datasets():
    sensor_path = kagglehub.dataset_download("image69of69pie/smartphone-sensor-dataset")
    iot_path = kagglehub.dataset_download("ziya07/iot-enabled-smart-lighting-dataset")
    uv_path = kagglehub.dataset_download("ziya07/solar-uv-radiation")
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    for path in [sensor_path, iot_path, uv_path]:
        for root, _, files in os.walk(path):
            for file in files: shutil.copy(os.path.join(root, file), raw_dir / file)

def download_openmeteo_data():
    external_dir = Path("data/external")
    external_dir.mkdir(parents=True, exist_ok=True)
    cities = {"London": (51.5, -0.12, "Europe/London"), "Singapore": (1.28, 103.85, "Asia/Singapore")}
    for city, (lat, lon, tz) in cities.items():
        params = {"latitude": lat, "longitude": lon, "hourly": ["uv_index", "shortwave_radiation", "direct_radiation", "cloud_cover"], "start_date": "2022-01-01", "end_date": "2023-12-31", "timezone": tz}
        r = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params)
        if r.status_code == 200:
            data = r.json()
            if "hourly" in data:
                df = pd.DataFrame(data["hourly"])
                df["time"] = pd.to_datetime(df["time"])
                df["latitude"] = lat; df["longitude"] = lon
                df.to_csv(external_dir / f"{city}_uv_hourly.csv", index=False)

if __name__ == "__main__":
    download_kaggle_datasets()
    download_openmeteo_data()
