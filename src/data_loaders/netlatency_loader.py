import os
import glob
import numpy as np
import pandas as pd

def load_seattle_data(repo_path='/tmp/NetLatency-Data', sampling_interval_ms=100):
    """
    Loads Seattle RTT data from the NetLatency-Data repository.
    The dataset consists of 688 time slices, each containing a 99x99 matrix.

    We flatten each matrix, extract valid RTT samples (e.g. > 0), and
    simulate a continuous time series stream.

    Args:
        repo_path (str): Path to the cloned NetLatency-Data repository.
        sampling_interval_ms (int): Synthetic sampling interval in milliseconds.

    Returns:
        pd.Series: RTT samples in seconds, indexed by synthetic timestamps.
    """
    seattle_dir = os.path.join(repo_path, 'Seattle')

    # Files are named like SeattleData_1, SeattleData_2, etc.
    # We need to sort them numerically to preserve the time-slice order.
    files = glob.glob(os.path.join(seattle_dir, 'SeattleData_*'))

    def get_num(filepath):
        basename = os.path.basename(filepath)
        num_str = basename.split('_')[1]
        return int(num_str)

    files = sorted(files, key=get_num)

    all_rtt_samples = []

    for f in files:
        # The files appear to be space-separated matrices
        try:
            mat = np.loadtxt(f)
            # Flatten and keep valid samples (e.g. diagonal is usually 0, or missing is -1)
            # We'll take elements > 0.
            samples = mat.flatten()
            valid_samples = samples[samples > 0]
            all_rtt_samples.extend(valid_samples)
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # Convert from list to array
    all_rtt_samples = np.array(all_rtt_samples)

    # Ensure we don't have too massive a dataset for memory/simulation speed
    # 688 slices * (99*99) ~ 6.7M samples. We'll sample/subsample or just keep them all.
    # Let's keep them all for robust simulation, it's manageable in pandas.
    # Actually, a smaller reproducible chunk is better for speed, let's use the first 100k samples.
    # No, the instructions say "The policy must monitor real-time RTT... over the same RTT trace".
    # I'll use the full array.

    # Convert ms to seconds
    rtt_seconds = all_rtt_samples / 1000.0

    # Create synthetic timestamps
    # Start at 2026-01-01 00:00:00
    start_time = pd.Timestamp('2026-01-01 00:00:00')
    time_deltas = pd.to_timedelta(np.arange(len(rtt_seconds)) * sampling_interval_ms, unit='ms')
    timestamps = start_time + time_deltas

    series = pd.Series(rtt_seconds, index=timestamps, name='RTT_seconds')

    return series

if __name__ == '__main__':
    s = load_seattle_data()
    print(f"Loaded {len(s)} RTT samples.")
    print(s.head())
