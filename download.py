import kagglehub
import shutil

print("Downloading 1...")
path1 = kagglehub.dataset_download('ziya07/uav-network-communication-dataset')
print(path1)
shutil.copytree(path1, "uav_qos_forecasting/data/raw", dirs_exist_ok=True)

print("Downloading 2...")
path2 = kagglehub.dataset_download('ziya07/uav-communication-monitoring-dataset')
print(path2)
shutil.copytree(path2, "uav_qos_forecasting/data/raw", dirs_exist_ok=True)

print("Downloading 3...")
path3 = kagglehub.dataset_download('ziya07/uav-network-optimization-dataset')
print(path3)
shutil.copytree(path3, "uav_qos_forecasting/data/raw", dirs_exist_ok=True)
