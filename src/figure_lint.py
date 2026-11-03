import os
import sys
import subprocess

def check_figures():
    forbidden = ["illustrative", "schematic", "placeholder", "dummy", "synthetic"]
    figures_dir = "outputs/figures"
    if not os.path.exists(figures_dir):
        return

    for f in os.listdir(figures_dir):
        if not (f.endswith(".pdf") or f.endswith(".png")):
            continue

        for word in forbidden:
            if word in f.lower():
                print(f"Forbidden word '{word}' in filename {f}")
                sys.exit(1)

        if f.endswith(".pdf"):
            res = subprocess.run(["pdftotext", os.path.join(figures_dir, f), "-"], capture_output=True, text=True)
            text = res.stdout.lower()
            for word in forbidden:
                if word in text:
                    print(f"Forbidden word '{word}' in PDF {f}")
                    sys.exit(1)

        # Check blank png
        if f.endswith(".png"):
            if os.path.getsize(os.path.join(figures_dir, f)) < 5000: # heuristic for near blank
                print(f"PNG file {f} is suspiciously small.")
                sys.exit(1)

    # Check manifest
    if not os.path.exists("outputs/figure_manifest.csv"):
        print("Missing figure_manifest.csv")
        sys.exit(1)

    print("Figure lint passed.")

if __name__ == "__main__":
    check_figures()
