import os
import json

def create_notebook(path):
    notebook = {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5
    }
    with open(path, 'w') as f:
        json.dump(notebook, f, indent=2)

dirs = [
    "ntl-poverty-estimation/data/raw/ntl",
    "ntl-poverty-estimation/data/raw/dhs",
    "ntl-poverty-estimation/data/raw/admin",
    "ntl-poverty-estimation/data/raw/modis_ndvi",
    "ntl-poverty-estimation/data/processed/ntl_rasters",
    "ntl-poverty-estimation/notebooks",
    "ntl-poverty-estimation/src",
    "ntl-poverty-estimation/outputs/figures",
    "ntl-poverty-estimation/outputs/tables",
    "ntl-poverty-estimation/outputs/datasets",
    "ntl-poverty-estimation/outputs/paper_assets"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

notebooks = [
    "01_data_ingestion.ipynb",
    "02_ntl_preprocessing.ipynb",
    "03_feature_engineering.ipynb",
    "04_model_training.ipynb",
    "05_evaluation_mapping.ipynb",
    "06_multimodal_fusion.ipynb"
]

for nb in notebooks:
    create_notebook(f"ntl-poverty-estimation/notebooks/{nb}")

print("Created structure and notebooks.")
