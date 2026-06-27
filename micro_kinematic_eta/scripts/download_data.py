import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATA_RAW_DIR

def main():
    print(f"Downloading dataset to {DATA_RAW_DIR} using kaggle API...")
    os.makedirs(DATA_RAW_DIR, exist_ok=True)

    try:
        import kaggle
        kaggle.api.dataset_download_files(
            "aysekoytak/ship-tracking-ais-data",
            path=DATA_RAW_DIR,
            unzip=True
        )
        print("Downloaded dataset successfully.")

        # Check files
        csv_file = os.path.join(DATA_RAW_DIR, 'ais_data.csv')
        if os.path.exists(csv_file):
            import pandas as pd
            df = pd.read_csv(csv_file)
            print("Data loaded successfully.")
            print(f"Row count: {len(df)}")
            print(f"Columns: {df.columns.tolist()}")
            if 'BaseDateTime' in df.columns:
                print(f"Date range: {df['BaseDateTime'].min()} to {df['BaseDateTime'].max()}")
            for col in ['SOG', 'COG', 'LAT', 'LON']:
                if col in df.columns:
                    null_pct = df[col].isnull().mean() * 100
                    print(f"% of rows with null {col}: {null_pct:.2f}%")

    except Exception as e:
        print(f"Error downloading with kaggle API: {e}")
        print("\nFallback instructions:")
        print("Manual download: https://www.kaggle.com/datasets/aysekoytak/ship-tracking-ais-data")
        print(f"Place CSV files in: {DATA_RAW_DIR}")
        print("Alternative: https://marinecadastre.gov/ais/ — download any monthly zone CSV")

if __name__ == "__main__":
    main()
