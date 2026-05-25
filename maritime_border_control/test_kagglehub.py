import kagglehub
try:
    path = kagglehub.dataset_download("thedevastator/detailed-labelled-fishing-trajectories-from-ais")
    print(f"Downloaded to {path}")
except Exception as e:
    print(f"Error: {e}")
