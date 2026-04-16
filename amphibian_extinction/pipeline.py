"""
End-to-End Amphibian Extinction Risk Modelling Pipeline
Integrates:
1. AmphiBIO (Ecological Traits) - Optional / Ablation
2. GBIF (Occurrences & IUCN Status) - Native
3. WorldClim (Bioclimatic variables) - Native
4. AmphibiaWeb (Taxonomy Validation)

Novel Methodological Contributions:
- Fully automated GBIF-native API pipeline.
- Spatially-blocked cross-validation for rigorous spatial generalization.
- Provisional prediction generation for Data Deficient (DD) species using constrained data (climate-only).
- Feature ablation study (Climate vs Climate+Traits).
"""

import os
import urllib.request
import zipfile
import json
import time
import requests
import pandas as pd
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor

from sklearn.model_selection import StratifiedKFold, GroupKFold, cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, confusion_matrix, roc_curve
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
import geopandas as gpd

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

os.makedirs('data', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# ---------------------------------------------------------
# 1. DATA ACQUISITION & VALIDATION
# ---------------------------------------------------------
print("=== Phase 1: Data Acquisition ===")

if not os.path.exists('data/AmphiBIO_v1.csv'):
    print("Downloading AmphiBIO...")
    url = "https://ndownloader.figshare.com/files/8828578"
    urllib.request.urlretrieve(url, 'data/AmphiBIO_v1.zip')
    with zipfile.ZipFile('data/AmphiBIO_v1.zip', 'r') as zip_ref:
        zip_ref.extractall('data')

if not os.path.exists('data/wc2.1_10m_bio/wc2.1_10m_bio_1.tif'):
    print("Downloading WorldClim (this may take a minute)...")
    url = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip"
    try:
        urllib.request.urlretrieve(url, 'data/wc2.1_10m_bio.zip')
        with zipfile.ZipFile('data/wc2.1_10m_bio.zip', 'r') as zip_ref:
            zip_ref.extractall('data/wc2.1_10m_bio')
    except Exception as e:
        print(f"Failed to download WorldClim: {e}")

if not os.path.exists('data/amphibiaweb.txt'):
    print("Downloading AmphibiaWeb Taxonomy...")
    url = "https://amphibiaweb.org/amphib_names.txt"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            with open('data/amphibiaweb.txt', 'wb') as f:
                f.write(res.content)
    except:
        pass

amphibio = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
species_list = amphibio['Species'].dropna().unique()

if os.path.exists('data/amphibiaweb.txt'):
    df_aw = pd.read_csv('data/amphibiaweb.txt', sep='\t', on_bad_lines='skip')
    aw_species = set((df_aw['genus'].astype(str) + " " + df_aw['species'].astype(str)).tolist())
    validated_species = [s for s in species_list if s in aw_species]
    if len(validated_species) > 500:
        species_list = validated_species

# ---------------------------------------------------------
# 2. GBIF API QUERIES (IUCN Status + Occurrences)
# ---------------------------------------------------------
print("=== Phase 2: GBIF Native Fetch & Extraction ===")

def fetch_gbif_data(species_name):
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}&class=Amphibia"
        res = requests.get(url, timeout=5).json()
        if 'usageKey' not in res: return None
        usage_key = res['usageKey']

        status = None
        prof_url = f"https://api.gbif.org/v1/species/{usage_key}/distributions"
        prof_res = requests.get(prof_url, timeout=5).json()
        for d in prof_res.get('results', []):
            if 'threatStatus' in d:
                status = d['threatStatus']
                break

        occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=5"
        occ_res = requests.get(occ_url, timeout=5).json()
        coords = [(r['decimalLongitude'], r['decimalLatitude']) for r in occ_res.get('results', []) if 'decimalLongitude' in r]

        return {"Species": species_name, "IUCN_Status": status, "coords": coords}
    except:
        return None

if not os.path.exists('data/species_data_gbif.json'):
    print("Fetching GBIF data (Sampling 1500 for demonstration)...")
    subset = species_list[:1500]
    gbif_results = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        for i, res in enumerate(executor.map(fetch_gbif_data, subset)):
            if res and res["IUCN_Status"]:
                gbif_results.append(res)
    with open('data/species_data_gbif.json', 'w') as f:
        json.dump(gbif_results, f)
else:
    with open('data/species_data_gbif.json') as f:
        gbif_results = json.load(f)

if len(gbif_results) == 0: exit(1)

# ---------------------------------------------------------
# 3. SPATIAL RASTER EXTRACTION
# ---------------------------------------------------------
print("=== Phase 3: WorldClim Raster Extraction ===")

if not os.path.exists('data/species_climate.csv'):
    rasters = {}
    for i in range(1, 20):
        try: rasters[f"bio_{i}"] = rasterio.open(f"data/wc2.1_10m_bio/wc2.1_10m_bio_{i}.tif")
        except: pass

    climate_data = []
    for item in gbif_results:
        species = item["Species"]
        coords = item.get("coords", [])
        climate_row = {"Species": species, "IUCN_Status": item["IUCN_Status"]}
        for var, src in rasters.items():
            vals = []
            for lon, lat in coords:
                try:
                    val = list(src.sample([(lon, lat)]))[0][0]
                    if val != src.nodata: vals.append(val)
                except: pass
            climate_row[f"{var}_mean"] = np.mean(vals) if vals else np.nan

        lons = [c[0] for c in coords]; lats = [c[1] for c in coords]
        climate_row["range_size_deg2"] = (max(lons) - min(lons)) * (max(lats) - min(lats)) if len(lons) > 1 else 0
        climate_row["mean_lon"] = np.mean(lons) if lons else 0
        climate_row["mean_lat"] = np.mean(lats) if lats else 0
        climate_data.append(climate_row)

    df_climate = pd.DataFrame(climate_data)
    df_climate.to_csv('data/species_climate.csv', index=False)
    for src in rasters.values(): src.close()
else:
    df_climate = pd.read_csv('data/species_climate.csv')

# ---------------------------------------------------------
# 4. PREPROCESSING & ABLATION SPLITTING
# ---------------------------------------------------------
print("=== Phase 4: Ablation Study & Spatial Data Prep ===")

df = amphibio.merge(df_climate, on='Species', how='inner')
df = df.dropna(subset=['IUCN_Status'])

# Map Threat Status & Data Deficient
threatened_classes = ['VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED']
non_threatened = ['LEAST_CONCERN', 'NEAR_THREATENED']
assessed_mask = df['IUCN_Status'].isin(threatened_classes + non_threatened)

# We use DD specifically for our provisional predictions
dd_mask = df['IUCN_Status'] == 'DATA_DEFICIENT'
df_dd = df[dd_mask].copy()
df_assessed = df[assessed_mask].copy()

df_assessed['Threatened'] = df_assessed['IUCN_Status'].apply(lambda x: 1 if x in threatened_classes else 0)

print(f"Total Assessed Species: {len(df_assessed)}. Total DD Species: {len(df_dd)}.")

traits = ['Fos', 'Ter', 'Aqu', 'Arb', 'Leaves', 'Flowers', 'Seeds', 'Fruits', 'Arthro', 'Vert', 'Diu', 'Noc', 'Crepu',
          'Wet_warm', 'Wet_cold', 'Dry_warm', 'Dry_cold', 'Body_mass_g', 'Age_at_maturity_min_y', 'Body_size_mm',
          'Longevity_max_y', 'Litter_size_max_n', 'Reproductive_output_y']
climate_features = [f'bio_{i}_mean' for i in range(1, 20)] + ['range_size_deg2']

for col in traits + climate_features:
    if col in df_assessed.columns:
        df_assessed[col] = pd.to_numeric(df_assessed[col], errors='coerce')
        df_dd[col] = pd.to_numeric(df_dd[col], errors='coerce')

climate_only_features = [f for f in climate_features if f in df_assessed.columns]
all_features = [f for f in traits + climate_features if f in df_assessed.columns]

# Impute
imputer_climate = SimpleImputer(strategy='median')
X_climate_assessed = imputer_climate.fit_transform(df_assessed[climate_only_features])
X_climate_dd = imputer_climate.transform(df_dd[climate_only_features])

imputer_all = SimpleImputer(strategy='median')
X_all_assessed = imputer_all.fit_transform(df_assessed[all_features])

y_assessed = df_assessed['Threatened'].values

# Add Spatial Clustering for GroupKFold CV
kmeans = KMeans(n_clusters=5, random_state=42)
spatial_groups = kmeans.fit_predict(df_assessed[['mean_lon', 'mean_lat']].fillna(0))

# ---------------------------------------------------------
# 5. SPATIALLY-BLOCKED CV & ABLATION STUDY
# ---------------------------------------------------------
print("=== Phase 5: Spatially-Blocked CV & Ablation ===")

xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
gkf = GroupKFold(n_splits=5)

# ABLATION 1: Climate Only
scaler_climate = StandardScaler()
X_c_scaled = scaler_climate.fit_transform(X_climate_assessed)
scores_climate = cross_val_score(xgb_model, X_c_scaled, y_assessed, groups=spatial_groups, cv=gkf, scoring='roc_auc')
print(f"-> Climate-Only Spatial CV ROC-AUC: {scores_climate.mean():.4f} (+/- {scores_climate.std() * 2:.4f})")

# ABLATION 2: Climate + Traits
scaler_all = StandardScaler()
X_a_scaled = scaler_all.fit_transform(X_all_assessed)
scores_all = cross_val_score(xgb_model, X_a_scaled, y_assessed, groups=spatial_groups, cv=gkf, scoring='roc_auc')
print(f"-> Climate+Traits Spatial CV ROC-AUC: {scores_all.mean():.4f} (+/- {scores_all.std() * 2:.4f})")



# Feature Importance Comparisons
xgb_climate = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_climate.fit(X_climate_assessed, y_assessed)
imp_climate = xgb_climate.feature_importances_
idx_climate = np.argsort(imp_climate)[::-1][:10]

xgb_all = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb_all.fit(X_all_assessed, y_assessed)
imp_all = xgb_all.feature_importances_
idx_all = np.argsort(imp_all)[::-1][:10]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

ax1.barh(range(10), imp_climate[idx_climate][::-1], align='center', color='skyblue')
ax1.set_yticks(range(10))
ax1.set_yticklabels([climate_only_features[i] for i in idx_climate][::-1])
ax1.set_title('Top 10 Features (Climate Only)')
ax1.set_xlabel('Relative Importance')

ax2.barh(range(10), imp_all[idx_all][::-1], align='center', color='lightcoral')
ax2.set_yticks(range(10))
ax2.set_yticklabels([all_features[i] for i in idx_all][::-1])
ax2.set_title('Top 10 Features (Climate + Traits)')
ax2.set_xlabel('Relative Importance')

plt.tight_layout()
plt.savefig('outputs/feature_importance_comparison.png')
plt.close()
print("Saved feature importance comparisons to outputs/feature_importance_comparison.png")


with open('outputs/ablation_results.txt', 'w') as f:
    f.write(f"Climate-Only Spatial CV ROC-AUC: {scores_climate.mean():.4f}\n")
    f.write(f"Climate+Traits Spatial CV ROC-AUC: {scores_all.mean():.4f}\n")

# ---------------------------------------------------------
# 6. DD PROVISIONAL PREDICTIONS (Novel Contribution)
# ---------------------------------------------------------
print("=== Phase 6: Provisional Risk Scoring for DD Species ===")

if len(df_dd) > 0:
    # Train full climate model
    xgb_climate = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    xgb_climate.fit(X_c_scaled, y_assessed)

    X_dd_scaled = scaler_climate.transform(X_climate_dd)
    dd_probs = xgb_climate.predict_proba(X_dd_scaled)[:, 1]
    dd_preds = xgb_climate.predict(X_dd_scaled)

    df_dd['Predicted_Risk_Probability'] = dd_probs
    df_dd['Predicted_Threat_Status'] = ['Threatened' if p == 1 else 'Non-Threatened' for p in dd_preds]

    df_dd[['Species', 'Predicted_Risk_Probability', 'Predicted_Threat_Status']].sort_values(by='Predicted_Risk_Probability', ascending=False).to_csv('outputs/dd_provisional_predictions.csv', index=False)
    print(f"Generated predictions for {len(df_dd)} DD species. Saved to outputs/dd_provisional_predictions.csv")

# ---------------------------------------------------------
# 7. FINAL EVALUATION & VISUALIZATION
# ---------------------------------------------------------
print("=== Phase 7: Generating Maps & Figures ===")
# Generate geographic map of the DD predictions
if len(df_dd) > 0:
    try:
        from urllib.request import urlretrieve
        urlretrieve("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip", "data/ne_110m.zip")
        world = gpd.read_file('zip://data/ne_110m.zip')

        fig, ax = plt.subplots(figsize=(15, 10))
        world.boundary.plot(ax=ax, linewidth=1, color='black')

        sns.scatterplot(data=df_dd[df_dd['Predicted_Threat_Status'] == 'Non-Threatened'], x='mean_lon', y='mean_lat', color='blue', alpha=0.6, s=50, label='Predicted Non-Threatened', ax=ax)
        sns.scatterplot(data=df_dd[df_dd['Predicted_Threat_Status'] == 'Threatened'], x='mean_lon', y='mean_lat', color='red', alpha=0.9, s=50, label='Predicted Threatened', ax=ax)

        plt.title('Predicted Extinction Risk for Data Deficient (DD) Amphibians')
        plt.legend()
        plt.tight_layout()
        plt.savefig('outputs/dd_geographic_risk_map.png')
        plt.close()
    except Exception as e:
        print(f"DD Map plotting failed: {e}")

print("=== Pipeline Complete ===")
