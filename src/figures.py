import os
import shutil

STYLE = {
    'primary': '#56B4E9',
    'secondary': '#E69F00'
}

def generate_figures():
    os.makedirs("outputs/figures", exist_ok=True)
    if os.path.exists("concept_methodology_overview.pdf"):
        shutil.copy("concept_methodology_overview.pdf", "outputs/figures/concept_methodology_overview.pdf")
    if os.path.exists("concept_methodology_overview.png"):
        shutil.copy("concept_methodology_overview.png", "outputs/figures/concept_methodology_overview.png")
