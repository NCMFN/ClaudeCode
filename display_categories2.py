import base64
import os

categories = {
    "1. System Architecture": ["outputs/architecture.png"],
    "2. Based on the Datasets": ["outputs/geographic_risk_map.png", "outputs/class_distribution.png"],
    "3. Based on the Methods": ["outputs/feature_importance.png", "outputs/correlation_heatmap.png"],
    "4. Based on the Results": ["outputs/feature_importance_comparison.png", "outputs/dd_geographic_risk_map.png", "outputs/roc_curves.png", "outputs/confusion_matrix.png"]
}

print("### Requested Figures for Download\n")

for cat, files in categories.items():
    print(f"#### {cat}\n")
    for f in files:
        if os.path.exists(f):
            with open(f, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                name = os.path.basename(f)
                print(f"**{name}**\n")
                print(f"![{name}](data:image/png;base64,{encoded})\n")
        else:
            pass # Just skip silently if we don't have it
