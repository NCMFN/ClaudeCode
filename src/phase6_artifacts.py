import pandas as pd
import os
import glob

def generate_manifests():
    # 1. Feature Operationalization Table
    features = [
        {'Feature': 'hour_cos', 'Proxy_For': 'Time of day cyclical patterns', 'Is_Temporal': True},
        {'Feature': 'hour_sin', 'Proxy_For': 'Time of day cyclical patterns', 'Is_Temporal': True},
        {'Feature': 'day_of_week', 'Proxy_For': 'Weekly routine patterns', 'Is_Temporal': True},
        {'Feature': 'event_count', 'Proxy_For': 'Volume of authentication activity', 'Is_Temporal': False},
        {'Feature': 'graph_degree', 'Proxy_For': 'Number of distinct systems connected', 'Is_Temporal': False},
        {'Feature': 'graph_betweenness', 'Proxy_For': 'Centrality in authentication graph', 'Is_Temporal': False},
        {'Feature': 'peer_z_score', 'Proxy_For': 'Deviation from peer group norm', 'Is_Temporal': False}
    ]
    df_feat = pd.DataFrame(features)

    note = "Note: LANL authentication schema does not directly encode 'digital sanitization' actions. The label comes entirely from redteam.txt.gz associations."
    with open("outputs/tables/feature_operationalization_note.txt", "w") as f:
        f.write(note)
    df_feat.to_csv("outputs/tables/feature_operationalization.csv", index=False)

    # 2. Paper Assets Manifest
    assets = []

    figures = glob.glob("outputs/figures/*.png")
    for fig in figures:
        assets.append({'Asset_Type': 'Figure', 'Path': fig})

    tables = glob.glob("outputs/tables/*.csv")
    for tab in tables:
        assets.append({'Asset_Type': 'Table', 'Path': tab})

    df_assets = pd.DataFrame(assets)
    df_assets.to_csv("outputs/paper_assets/paper_assets_manifest.csv", index=False)

if __name__ == "__main__":
    generate_manifests()
    print("Phase 6 complete.")
