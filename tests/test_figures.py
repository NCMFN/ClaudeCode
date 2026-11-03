import os
import subprocess

def test_figure_lint():
    forbidden = ["illustrative", "schematic", "placeholder", "dummy", "synthetic"]
    figures_dir = "outputs/figures"
    if not os.path.exists(figures_dir):
        return

    for f in os.listdir(figures_dir):
        if not (f.endswith(".pdf") or f.endswith(".png")):
            continue

        for word in forbidden:
            assert word not in f.lower(), f"Forbidden word '{word}' in filename {f}"

        # check pdftotext
        if f.endswith(".pdf"):
            res = subprocess.run(["pdftotext", os.path.join(figures_dir, f), "-"], capture_output=True, text=True)
            text = res.stdout.lower()
            for word in forbidden:
                assert word not in text, f"Forbidden word '{word}' in PDF {f}"
