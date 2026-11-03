import zipfile
import os

def main():
    manifest_path = "outputs/paper_assets/paper_assets_manifest.csv"
    bundle_path = "outputs/paper_assets/paper_assets_bundle.zip"

    if os.path.exists(manifest_path):
        with zipfile.ZipFile(bundle_path, 'w') as zf:
            zf.write(manifest_path)
            with open(manifest_path, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]: # skip header
                    path = line.split(',')[0]
                    if os.path.exists(path):
                        zf.write(path)

if __name__ == "__main__":
    main()
