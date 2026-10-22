import kagglehub
import shutil
import os
import logging
from datetime import datetime

# Setup logging
os.makedirs("results/logs", exist_ok=True)
logging.basicConfig(
    filename="results/logs/download.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    start_time = datetime.now()
    logging.info("Starting dataset download")
    print("Downloading dataset...")

    try:
        # Download latest version
        path = kagglehub.dataset_download("molloysarahmaria/iot-enabled-smart-grid-dataset")
        print("Path to dataset files:", path)
        logging.info(f"Downloaded to {path}")

        # Copy files to data/primary
        dest_dir = "data/primary"
        os.makedirs(dest_dir, exist_ok=True)

        for file in os.listdir(path):
            src_file = os.path.join(path, file)
            dest_file = os.path.join(dest_dir, file)
            shutil.copy2(src_file, dest_file)
            print(f"Copied {file} to {dest_dir}")
            logging.info(f"Copied {file} to {dest_dir}")

        end_time = datetime.now()
        logging.info(f"Download completed successfully in {end_time - start_time}")

    except Exception as e:
        logging.error(f"Failed to download dataset: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
