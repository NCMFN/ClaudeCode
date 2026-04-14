import os
import requests
from tqdm import tqdm

# Configuration section: customize the artifact URLs and types
ARTIFACTS = [
    {'url': 'https://example.com/artifact1.zip', 'filename': 'artifact1.zip'},
    {'url': 'https://example.com/artifact2.tar.gz', 'filename': 'artifact2.tar.gz'},
]

def download_file(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        with open(filename, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True) as bar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                bar.update(len(data))
        print(f'\nDownloaded: {filename}')
    else:
        print(f'Failed to download {filename}. Status code: {response.status_code}')

if __name__ == '__main__':
    for artifact in ARTIFACTS:
        download_file(artifact['url'], artifact['filename'])
