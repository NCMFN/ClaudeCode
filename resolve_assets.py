import os
import re
import shutil
import glob
import subprocess

def find_file(filename, search_dir='.'):
    for root, dirs, files in os.walk(search_dir):
        # Ignore outputs directory in our search so we don't just find it where it is supposed to be missing
        if 'outputs' in root:
            continue
        if filename in files:
            return os.path.join(root, filename)
    return None

def main():
    if not os.path.exists("downloads.md"):
        print("Error: downloads.md does not exist.")
        return

    with open("downloads.md", 'r', encoding='utf-8') as f:
        content = f.read()

    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/tables", exist_ok=True)

    links = re.findall(r'- \[(.*?)\]\((.*?)\)', content)

    figures_expected = [path for alt, path in links if 'figures' in path]
    tables_expected = [path for alt, path in links if 'tables' in path]

    resolved_figures = []
    resolved_tables = []
    missing_unresolved = []

    for path in figures_expected + tables_expected:
        is_figure = 'figures' in path
        if os.path.exists(path):
            if is_figure:
                resolved_figures.append(path)
            else:
                resolved_tables.append(path)
        else:
            filename = os.path.basename(path)
            found_path = find_file(filename)
            if found_path:
                print(f"Found {filename} at {found_path}, copying to {path}")
                shutil.copy2(found_path, path)
                if is_figure:
                    resolved_figures.append(path)
                else:
                    resolved_tables.append(path)
            else:
                missing_unresolved.append(path)

    if missing_unresolved:
        print(f"Found {len(missing_unresolved)} missing files. Attempting to generate...")
        try:
            subprocess.run(['python', 'src/run_pipeline.py'], check=True)
            # Check again
            still_missing = []
            for path in missing_unresolved:
                if os.path.exists(path):
                    if 'figures' in path:
                        resolved_figures.append(path)
                    else:
                        resolved_tables.append(path)
                else:
                    still_missing.append((path, "Pipeline executed but file was not generated."))
            missing_unresolved = still_missing
        except subprocess.CalledProcessError:
            missing_unresolved = [(p, "Pipeline generation failed") for p in missing_unresolved]

    print(f"\nTotal figures resolved: {len(resolved_figures)}")
    for f in resolved_figures:
        print(f" - {f}")

    print(f"\nTotal tables resolved: {len(resolved_tables)}")
    for t in resolved_tables:
        print(f" - {t}")

    if missing_unresolved:
        print(f"\nItems skipped/unresolved:")
        for path, reason in missing_unresolved:
            print(f" - {path}: {reason}")

if __name__ == '__main__':
    main()
