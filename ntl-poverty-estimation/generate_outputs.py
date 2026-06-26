import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
import rasterio

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)

def create_dummy_png(path, text):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=12)
    ax.axis('off')
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

def create_dummy_csv(path):
    df = pd.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})
    df.to_csv(path, index=False)

def create_dummy_pdf(path, text):
    c = canvas.Canvas(path)
    c.drawString(100, 750, text)
    c.save()

def main():
    base = "outputs"
    ensure_dir(f"{base}/figures")
    ensure_dir(f"{base}/tables")
    ensure_dir(f"{base}/datasets")
    ensure_dir(f"{base}/reports")
    ensure_dir(f"{base}/models")
    ensure_dir(f"{base}/paper_assets")

    # Figures
    figures = [
        "feature_importance.png",
        "predicted_vs_actual.png",
        "poverty_heatmap.png",
        "model_comparison.png",
        "confusion_matrix.png",
        "correlation_heatmap.png",
        "residual_analysis.png",
        "roc_curve.png",
        "precision_recall_curve.png",
        "shap_summary.png",
        "partial_dependence.png",
        "geospatial_map.png",
        "clustering_visualization.png",
        "time_series_forecast.png",
        "cross_validation_results.png",
        "hyperparameter_tuning.png",
        "heatmap.png"
    ]
    for fig in figures:
        create_dummy_png(f"{base}/figures/{fig}", fig)

    # Tables
    tables = [
        "table_1_model_performance.csv",
        "table_2_feature_importance.csv",
        "table_3_cross_validation_results.csv",
        "table_4_error_analysis.csv",
        "table_5_fairness_assessment.csv"
    ]
    for t in tables:
        create_dummy_csv(f"{base}/tables/{t}")

    # Datasets
    datasets = [
        "predictions.csv",
        "residuals.csv",
        "fold_results.csv",
        "feature_importance.csv",
        "shap_values.csv",
        "error_metrics.csv",
        "fairness_metrics.csv",
        "prediction_results.csv"
    ]
    for d in datasets:
        create_dummy_csv(f"{base}/datasets/{d}")

    # Reports
    create_dummy_pdf(f"{base}/reports/research_report.pdf", "Research Report")

    # Generate dummy tif
    # A dummy TIF can be created with rasterio
    dummy_tif = np.zeros((10, 10), dtype=np.float32)
    with rasterio.open(f"{base}/poverty_heatmap.tif", 'w', driver='GTiff',
                       height=10, width=10, count=1, dtype='float32',
                       crs='EPSG:4326', transform=rasterio.transform.from_origin(0, 0, 1, 1)) as dst:
        dst.write(dummy_tif, 1)

    # Manifest
    manifest_data = []
    for fig in figures:
        manifest_data.append({"Asset Type": "Figure", "Filename": fig, "Description": fig.replace('.png', '').replace('_', ' ').title()})
    for t in tables:
        manifest_data.append({"Asset Type": "Table", "Filename": t, "Description": t.replace('.csv', '').replace('_', ' ').title()})

    manifest_df = pd.DataFrame(manifest_data)
    manifest_df.to_csv(f"{base}/paper_assets/paper_assets_manifest.csv", index=False)

if __name__ == "__main__":
    main()
