import os
import glob
import logging
import csv
import PyPDF2
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FORBIDDEN_WORDS = ["illustrative", "schematic - not measured", "placeholder", "dummy"]

def lint_figures(figures_dir: str):
    logger.info("Starting figure linting...")

    manifest_path = os.path.join('outputs', 'figure_manifest.csv')

    manifest = []
    has_errors = False

    for f in os.listdir(figures_dir):
        if not f.endswith('.png') and not f.endswith('.pdf'):
            continue

        filepath = os.path.join(figures_dir, f)
        fig_type = "CONCEPTUAL" if "concept" in f else "MEASURED"

        if fig_type == "MEASURED":
            if not os.path.exists('outputs/provenance.json'):
                logger.error(f"{f} is MEASURED but provenance.json is missing.")
                has_errors = True

        if f.endswith('.png'):
            # Check if nearly blank
            img = Image.open(filepath).convert('L')
            arr = np.array(img)
            # 255 is white
            white_ratio = np.sum(arr > 250) / arr.size
            if white_ratio > 0.98:
                 logger.error(f"{f} appears to be nearly blank.")
                 has_errors = True

        if f.endswith('.pdf'):
            # Check text
            try:
                with open(filepath, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    text_lower = text.lower()
                    for word in FORBIDDEN_WORDS:
                        if word in text_lower:
                            logger.error(f"{f} contains forbidden word: {word}")
                            has_errors = True
            except Exception as e:
                logger.error(f"Failed to read PDF {f}: {e}")

        manifest.append({
            'filename': f,
            'type': fig_type,
            'source_script': 'src/figures.py',
            'status_at_generation': 'UNKNOWN'
        })

    os.makedirs('outputs', exist_ok=True)
    with open(manifest_path, 'w', newline='') as csvfile:
        fieldnames = ['filename', 'type', 'source_script', 'source_data_hash', 'status_at_generation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for m in manifest:
             m['source_data_hash'] = ''
             writer.writerow(m)

    if has_errors:
         raise RuntimeError("Figure linting failed. See logs.")

    logger.info("Figure linting passed.")

if __name__ == "__main__":
    lint_figures("outputs/figures")
