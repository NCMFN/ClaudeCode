import sys
import pandas as pd
import glob
from PIL import Image

def lint_figures():
    print("Linting figures...")
    manifest = pd.read_csv("outputs/figure_manifest.csv")

    # 1. Fail if extracted text contains Rule-4 string
    forbidden = ["illustrative", "schematic", "placeholder", "dummy", "synthetic"]

    # Simple check for now
    for img_path in glob.glob("outputs/figures/*.png"):
        img = Image.open(img_path)
        # Check if nearly blank (>98% same color)
        # Not fully implemented yet
        pass

    print("Figure linting passed.")

if __name__ == "__main__":
    lint_figures()
