import kagglehub
import shutil

path1 = kagglehub.dataset_download('ziya07/uav-network-communication-dataset')
shutil.copytree(path1, "uav_qos_forecasting/data/raw", dirs_exist_ok=True)

path2 = kagglehub.dataset_download('ziya07/uav-communication-monitoring-dataset')
shutil.copytree(path2, "uav_qos_forecasting/data/raw", dirs_exist_ok=True)

path3 = kagglehub.dataset_download('ziya07/uav-network-optimization-dataset')
shutil.copytree(path3, "uav_qos_forecasting/data/raw", dirs_exist_ok=True)
