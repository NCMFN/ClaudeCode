import os
import pandas as pd
import numpy as np

def load_seattle_rtt_series(data_dir: str, start_time: str = '2024-01-01T00:00:00Z', interval_ms: int = 1000) -> pd.Series:
    """
    Loads the Seattle NetLatency dataset and reshapes it into a time series of RTT samples.

    The dataset consists of 688 time slices, each containing a 99x99 RTT matrix.
    Since we need a single time series of RTT representing latency at each step,
    we randomly sample one non-zero RTT from each matrix.

    Args:
        data_dir: Path to the Seattle dataset directory (e.g., 'NetLatency-Data/Seattle').
        start_time: Synthetic start timestamp for the time series.
        interval_ms: Interval between samples in milliseconds.

    Returns:
        pd.Series: RTT values in seconds, indexed by synthetic DatetimeIndex.
    """
    # Find all SeattleData_t files and sort them numerically by t
    files = [f for f in os.listdir(data_dir) if f.startswith('SeattleData_')]
    files.sort(key=lambda x: int(x.split('_')[1]))

    rtt_samples = []

    # Set seed for reproducible extraction
    rng = np.random.default_rng(42)

    for filename in files:
        filepath = os.path.join(data_dir, filename)
        # Read the matrix. Files are tab-separated.
        try:
            # pd.read_csv is faster but some lines might have variable whitespace.
            # The data format uses tabs.
            df = pd.read_csv(filepath, sep='\t', header=None)

            # Convert to numpy array and flatten
            matrix = df.values.flatten()

            # Filter out zeros (self-RTT or missing data)
            non_zero = matrix[matrix > 0]

            if len(non_zero) > 0:
                # Sample one RTT randomly
                sample = rng.choice(non_zero)
                rtt_samples.append(sample)
            else:
                # Fallback if matrix is empty or all zeros
                rtt_samples.append(np.nan)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            rtt_samples.append(np.nan)

    # Forward-fill any NaNs in case of completely empty slices
    s = pd.Series(rtt_samples)
    s = s.ffill().bfill()

    # The RTTs in the dataset are in milliseconds or seconds? Let's check magnitude.
    # Looking at the sample (0.17, 0.32, ...), they are likely in seconds (or hundreds of ms).
    # Wait, the prompt says "t is the measured classical RTT latency for that time step ... in seconds".
    # Since values are 0.17, 0.49, etc., these are in seconds. We keep them as is.

    # Generate synthetic timestamps
    timestamps = pd.date_range(start=start_time, periods=len(s), freq=f'{interval_ms}ms')
    s.index = timestamps
    s.name = 'rtt_seconds'

    return s

if __name__ == "__main__":
    # Test execution
    data_path = os.path.join(os.path.dirname(__file__), '..', 'NetLatency-Data', 'Seattle')
    if os.path.exists(data_path):
        ts = load_seattle_rtt_series(data_path)
        print("Loaded RTT Time Series:")
        print(ts.head())
        print(f"Length: {len(ts)}")
        print(f"Mean RTT: {ts.mean():.4f} s")
    else:
        print(f"Dataset path not found: {data_path}")
