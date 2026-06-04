import kagglehub
import shutil
import os

path = kagglehub.dataset_download("ziya07/smart-manufacturing-iot-cloud-monitoring-dataset")
print("Path to dataset files:", path)
for f in os.listdir(path):
    if f.endswith('.csv'):
        shutil.copy(os.path.join(path, f), 'data/')
