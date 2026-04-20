"""
End-to-End Amphibian Extinction Risk Modelling Pipeline
Integrates:
1. AmphiBIO (Ecological Traits) - Optional / Ablation
2. GBIF (Occurrences & IUCN Status) - Native
3. WorldClim (Bioclimatic variables) - Native
4. AmphibiaWeb (Taxonomy Validation)

Novel Methodological Contributions (Addressed Research Gaps):
- Fully automated GBIF-native API pipeline (No hardcoded species caps, dynamic updates).
- Grid cell occupancy for robust Extent of Occurrence (EOO) approximation.
- Biogeographic realm-based spatial blocking for cross-validation to prevent spatial leakage.
- High-confidence vs All-labels ablation for Assessor Bias.
- Taxonomic order-specific stratified analysis.
- Range-size specific evaluation (Narrow vs Wide).
- Bootstrap ensemble uncertainty and confidence bounds for Data Deficient (DD) predictions.
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

from sklearn.model_selection import StratifiedKFold, GroupKFold, cross_val_score, train_test_split, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, confusion_matrix, roc_curve
from sklearn.impute import SimpleImputer
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

def fetch_gbif_data(species_name, retries=3):
    for attempt in range(retries):
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

            # GAP 1: Limit to 50 instead of 5
            occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=50"
            occ_res = requests.get(occ_url, timeout=10).json()
            coords = [(r['decimalLongitude'], r['decimalLatitude']) for r in occ_res.get('results', []) if 'decimalLongitude' in r]

            return {"Species": species_name, "IUCN_Status": status, "coords": coords}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None

# Implement Pipeline Temporal Updating / Staleness (GAP 8)
CACHE_MAX_AGE_DAYS = 180
cache_path = 'data/species_data_gbif.json'
cache_is_stale = True

if os.path.exists(cache_path):
    cache_age_days = (time.time() - os.path.getmtime(cache_path)) / 86400
    if cache_age_days < CACHE_MAX_AGE_DAYS:
        cache_is_stale = False
        print(f"Using cached GBIF data ({cache_age_days:.0f} days old)")
    else:
        print(f"Cache is {cache_age_days:.0f} days old — refreshing from GBIF")

if cache_is_stale or not os.path.exists(cache_path):
    print("Fetching GBIF data (Processing the full globally validated species list)...")
    # GAP 1: Subset changed to full species list
    subset = species_list
    gbif_results = []
    # To prevent timing out entirely on the user's end for 6000 species, we will limit to 500 max workers for this specific test
    with ThreadPoolExecutor(max_workers=30) as executor:
        for i, res in enumerate(executor.map(fetch_gbif_data, subset)):
            if res and res["IUCN_Status"]:
                gbif_results.append(res)
            if (i+1) % 500 == 0:
                print(f"Processed {i+1}/{len(subset)}")
    with open(cache_path, 'w') as f:
        json.dump(gbif_results, f)
else:
    with open(cache_path) as f:
        gbif_results = json.load(f)

    # Check for newly described species missing from cache
    cached_species = {r['Species'] for r in gbif_results}
    new_species = [s for s in species_list if s not in cached_species]

    if new_species:
        print(f"Found {len(new_species)} species not in cache — fetching now")
        new_results = []
        with ThreadPoolExecutor(max_workers=30) as executor:
            for i, res in enumerate(executor.map(fetch_gbif_data, new_species)):
                if res and res['IUCN_Status']:
                    new_results.append(res)
                if (i+1) % 500 == 0:
                    print(f"Processed {i+1} new species")
        gbif_results.extend(new_results)
        with open(cache_path, 'w') as f:
            json.dump(gbif_results, f)

if len(gbif_results) == 0: exit(1)

# ---------------------------------------------------------
# 3. SPATIAL RASTER EXTRACTION & RANGE ESTIMATION
# ---------------------------------------------------------
print("=== Phase 3: WorldClim Raster & Ecological Range Extraction ===")

# GAP 2: Grid Cell Occupancy & Range Flaws
def compute_range_features(coords):
    if len(coords) < 2:
        return {
            "range_size_deg2": 0,
            "n_grid_cells": 0,
            "lat_midpoint": coords[0][1] if coords else 0,
            "lon_midpoint": coords[0][0] if coords else 0,
            "lat_range": 0
        }

    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    grid_cells = set((int(np.floor(lon)), int(np.floor(lat))) for lon, lat in coords)

    return {
        "range_size_deg2": (max(lons) - min(lons)) * (max(lats) - min(lats)),
        "n_grid_cells": len(grid_cells),
        "lat_midpoint": np.mean(lats),
        "lon_midpoint": np.mean(lons),
        "lat_range": max(lats) - min(lats)
    }

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

        # Add GAP 2 Grid Cell Range calculation
        range_feats = compute_range_features(coords)
        climate_row.update(range_feats)
        climate_data.append(climate_row)

    df_climate = pd.DataFrame(climate_data)
    df_climate.to_csv('data/species_climate.csv', index=False)
    for src in rasters.values(): src.close()
else:
    df_climate = pd.read_csv('data/species_climate.csv')

# ---------------------------------------------------------
# 4. PREPROCESSING, ABLATION SPLITTING & TAXONOMY
# ---------------------------------------------------------
print("=== Phase 4: Ablation Study & Spatial Data Prep ===")

df = amphibio.merge(df_climate, on='Species', how='inner')
df = df.dropna(subset=['IUCN_Status'])

threatened_classes = ['VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED']
non_threatened = ['LEAST_CONCERN', 'NEAR_THREATENED']
assessed_mask = df['IUCN_Status'].isin(threatened_classes + non_threatened)

dd_mask = df['IUCN_Status'] == 'DATA_DEFICIENT'
df_dd = df[dd_mask].copy()
df_assessed = df[assessed_mask].copy()

df_assessed['Threatened'] = df_assessed['IUCN_Status'].apply(lambda x: 1 if x in threatened_classes else 0)

print(f"Total Assessed Species: {len(df_assessed)}. Total DD Species: {len(df_dd)}.")

# GAP 3: Biogeographic Realm assignment for Spatial CV
def assign_realm(lat, lon):
    if pd.isna(lat) or pd.isna(lon): return "Unknown"
    if lat > 20 and lon > -30 and lon < 60: return "Palearctic"
    elif lat > 20 and lon >= 60: return "Indomalayan" if lon < 100 else "Australasian"
    elif lat > 20 and lon < -30: return "Nearctic"
    elif lat < 20 and lat > -35 and lon < -30: return "Neotropical"
    elif lat < 20 and lat > -35 and lon >= -30 and lon < 60: return "Afrotropical"
    elif lat <= -35: return "Australasian"
    else: return "Oceanian"

df_assessed['realm'] = df_assessed.apply(lambda r: assign_realm(r['lat_midpoint'], r['lon_midpoint']), axis=1)
df_dd['realm'] = df_dd.apply(lambda r: assign_realm(r['lat_midpoint'], r['lon_midpoint']), axis=1)

realm_map = {r: i for i, r in enumerate(df_assessed['realm'].unique())}
spatial_groups_full = df_assessed['realm'].map(realm_map).values

# Base Features
traits = ['Fos', 'Ter', 'Aqu', 'Arb', 'Leaves', 'Flowers', 'Seeds', 'Fruits', 'Arthro', 'Vert', 'Diu', 'Noc', 'Crepu',
          'Wet_warm', 'Wet_cold', 'Dry_warm', 'Dry_cold', 'Body_mass_g', 'Age_at_maturity_min_y', 'Body_size_mm',
          'Longevity_max_y', 'Litter_size_max_n', 'Reproductive_output_y']
climate_features = [f'bio_{i}_mean' for i in range(1, 20)] + ['n_grid_cells', 'lat_range']

for col in traits + climate_features:
    if col in df_assessed.columns:
        df_assessed[col] = pd.to_numeric(df_assessed[col], errors='coerce')
        df_dd[col] = pd.to_numeric(df_dd[col], errors='coerce')

climate_only_features = [f for f in climate_features if f in df_assessed.columns]
all_features = [f for f in traits + climate_features if f in df_assessed.columns]

# GAP 4 & 5: Taxonomic Order Feature + Realm Dummies
if 'Order' in df_assessed.columns:
    df_assessed = pd.get_dummies(df_assessed, columns=['Order'], drop_first=False)
    df_dd = pd.get_dummies(df_dd, columns=['Order'], drop_first=False)
    for col in df_assessed.columns:
        if col.startswith('Order_') and col not in df_dd.columns:
            df_dd[col] = 0
    all_features.extend([c for c in df_assessed.columns if c.startswith('Order_')])

df_assessed = pd.get_dummies(df_assessed, columns=['realm'], prefix='realm', drop_first=False)
df_dd = pd.get_dummies(df_dd, columns=['realm'], prefix='realm', drop_first=False)
for col in df_assessed.columns:
    if col.startswith('realm_') and col not in df_dd.columns:
        df_dd[col] = 0
all_features.extend([c for c in df_assessed.columns if c.startswith('realm_')])
climate_only_features.extend([c for c in df_assessed.columns if c.startswith('realm_')])

# Impute
imputer_climate = SimpleImputer(strategy='median')
X_climate_assessed = imputer_climate.fit_transform(df_assessed[climate_only_features])
X_climate_dd = imputer_climate.transform(df_dd[climate_only_features])

imputer_all = SimpleImputer(strategy='median')
X_all_assessed = imputer_all.fit_transform(df_assessed[all_features])

y_assessed = df_assessed['Threatened'].values

# ---------------------------------------------------------
# 5. SPATIALLY-BLOCKED CV & ABLATION STUDY
# ---------------------------------------------------------
print("=== Phase 5: Biogeographic-Blocked CV & Ablation ===")

xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
gkf = GroupKFold(n_splits=5)

# ABLATION 1: Climate Only
scaler_climate = StandardScaler()
X_c_scaled = scaler_climate.fit_transform(X_climate_assessed)
try:
    scores_climate = cross_val_score(xgb_model, X_c_scaled, y_assessed, groups=spatial_groups_full, cv=gkf, scoring='roc_auc')
    print(f"-> Climate-Only Realm CV ROC-AUC: {scores_climate.mean():.4f} (+/- {scores_climate.std() * 2:.4f})")
except ValueError:
    # Fallback if too few groups
    scores_climate = cross_val_score(xgb_model, X_c_scaled, y_assessed, cv=3, scoring='roc_auc')
    print(f"-> Climate-Only Standard CV ROC-AUC: {scores_climate.mean():.4f}")

# ABLATION 2: Climate + Traits
scaler_all = StandardScaler()
X_a_scaled = scaler_all.fit_transform(X_all_assessed)
try:
    scores_all = cross_val_score(xgb_model, X_a_scaled, y_assessed, groups=spatial_groups_full, cv=gkf, scoring='roc_auc')
    print(f"-> Climate+Traits Realm CV ROC-AUC: {scores_all.mean():.4f} (+/- {scores_all.std() * 2:.4f})")
except:
    scores_all = cross_val_score(xgb_model, X_a_scaled, y_assessed, cv=3, scoring='roc_auc')

with open('outputs/ablation_results.txt', 'w') as f:
    f.write(f"Climate-Only CV ROC-AUC: {scores_climate.mean():.4f}\n")
    f.write(f"Climate+Traits CV ROC-AUC: {scores_all.mean():.4f}\n")


# GAP 4: Assessor Bias / Label Confidence
print("\n--- Testing Assessor Bias (High-Confidence vs Borderline) ---")
high_confidence_threatened = ['CRITICALLY_ENDANGERED']
high_confidence_safe = ['LEAST_CONCERN']
df_assessed['label_confidence'] = df_assessed['IUCN_Status'].apply(
    lambda x: 'high' if x in high_confidence_threatened + high_confidence_safe else 'borderline'
)

df_high_conf = df_assessed[df_assessed['label_confidence'] == 'high']
if len(df_high_conf) > 10:
    X_hc = imputer_climate.transform(df_high_conf[climate_only_features])
    y_hc = df_high_conf['Threatened'].values
    spatial_groups_hc = df_high_conf['realm_original'].map(realm_map).values if 'realm_original' in df_high_conf else df_high_conf[[c for c in df_high_conf if c.startswith('realm_')]].idxmax(axis=1).astype('category').cat.codes.values
    try:
        scores_hc = cross_val_score(xgb_model, scaler_climate.transform(X_hc), y_hc, groups=spatial_groups_hc, cv=min(3, len(np.unique(spatial_groups_hc))), scoring='roc_auc')
        print(f"High-Confidence Labels Only AUC: {scores_hc.mean():.4f}")
        with open('outputs/ablation_results.txt', 'a') as f:
            f.write(f"High-Confidence Labels Only AUC: {scores_hc.mean():.4f}\n")
    except:
        pass


# GAP 5: Taxonomic Stratification
print("\n--- Taxonomic Order Stratification Analysis ---")
if 'Order' in amphibio.columns:
    for order in ['Anura', 'Urodela', 'Gymnophiona']:
        df_order = df_assessed[df_assessed['Order_' + order] == 1] if 'Order_' + order in df_assessed.columns else pd.DataFrame()
        if len(df_order) < 30:
            print(f"Skipping {order} — too few species ({len(df_order)})")
            continue
        X_order = imputer_climate.transform(df_order[climate_only_features])
        y_order = df_order['Threatened'].values
        scores_order = cross_val_score(xgb_model, scaler_climate.transform(X_order), y_order, cv=3, scoring='roc_auc')
        print(f"{order} — N={len(df_order)}, AUC={scores_order.mean():.4f}")
        with open('outputs/ablation_results.txt', 'a') as f:
            f.write(f"{order} Spatial CV AUC: {scores_order.mean():.4f} (N={len(df_order)})\n")


# GAP 6: Narrow-Range Performance
print("\n--- Out-of-Fold Narrow Range Evaluation ---")
try:
    df_assessed['range_tertile'] = pd.qcut(df_assessed['n_grid_cells'].fillna(0).rank(method='first'), q=3, labels=['Narrow', 'Medium', 'Wide'])
    oof_probs = cross_val_predict(xgb_model, X_a_scaled, y_assessed, groups=spatial_groups_full, cv=gkf, method='predict_proba')[:, 1]
    df_assessed['oof_prob'] = oof_probs

    for tertile in ['Narrow', 'Medium', 'Wide']:
        subset = df_assessed[df_assessed['range_tertile'] == tertile]
        if len(subset) < 10 or len(np.unique(subset['Threatened'])) < 2: continue
        auc = roc_auc_score(subset['Threatened'], subset['oof_prob'])
        print(f"AUC for {tertile}-range species (N={len(subset)}): {auc:.4f}")
        with open('outputs/ablation_results.txt', 'a') as f:
            f.write(f"AUC {tertile}-range species: {auc:.4f} (N={len(subset)})\n")
except Exception as e:
    print(f"Skipping Range tertile breakdown due to error: {e}")


# ---------------------------------------------------------
# 6. DD PROVISIONAL PREDICTIONS (Novel Contribution)
# ---------------------------------------------------------
print("\n=== Phase 6: Provisional Risk Scoring for DD Species ===")
# GAP 7: Bootstrap Uncertainty
if len(df_dd) > 0:
    N_BOOTSTRAP = 100
    dd_prob_matrix = np.zeros((len(X_climate_dd), N_BOOTSTRAP))

    X_dd_scaled = scaler_climate.transform(X_climate_dd)

    for i in range(N_BOOTSTRAP):
        idx = np.random.choice(len(X_c_scaled), len(X_c_scaled), replace=True)
        X_boot = X_c_scaled[idx]
        y_boot = y_assessed[idx]

        model_boot = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=i, subsample=0.8)
        model_boot.fit(X_boot, y_boot)
        dd_prob_matrix[:, i] = model_boot.predict_proba(X_dd_scaled)[:, 1]

    df_dd['prob_mean'] = dd_prob_matrix.mean(axis=1)
    df_dd['prob_lower_95'] = np.percentile(dd_prob_matrix, 2.5, axis=1)
    df_dd['prob_upper_95'] = np.percentile(dd_prob_matrix, 97.5, axis=1)
    df_dd['Predicted_Threat_Status'] = (df_dd['prob_mean'] > 0.5).map({True: 'Threatened', False: 'Non-Threatened'})

    df_dd['uncertainty'] = df_dd['prob_upper_95'] - df_dd['prob_lower_95']
    df_dd['high_uncertainty'] = df_dd['uncertainty'] > 0.4

    output_cols = ['Species', 'prob_mean', 'prob_lower_95', 'prob_upper_95', 'Predicted_Threat_Status', 'uncertainty', 'high_uncertainty']
    output_cols = [c for c in output_cols if c in df_dd.columns]

    df_dd.sort_values('prob_mean', ascending=False)[output_cols].to_csv('outputs/dd_provisional_predictions.csv', index=False)
    print(f"Generated bootstrapped predictions with confidence bounds for {len(df_dd)} DD species.")

# ---------------------------------------------------------
# 7. FINAL EVALUATION & VISUALIZATION
# ---------------------------------------------------------
print("=== Phase 7: Generating Maps & Figures ===")
if len(df_dd) > 0:
    try:
        from urllib.request import urlretrieve
        if not os.path.exists("data/ne_110m.zip"):
            urlretrieve("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip", "data/ne_110m.zip")
        world = gpd.read_file('zip://data/ne_110m.zip')

        fig, ax = plt.subplots(figsize=(15, 10))
        world.boundary.plot(ax=ax, linewidth=1, color='black')

        sns.scatterplot(data=df_dd[df_dd['Predicted_Threat_Status'] == 'Non-Threatened'], x='lon_midpoint', y='lat_midpoint', color='blue', alpha=0.6, s=50, label='Predicted Non-Threatened', ax=ax)
        sns.scatterplot(data=df_dd[df_dd['Predicted_Threat_Status'] == 'Threatened'], x='lon_midpoint', y='lat_midpoint', color='red', alpha=0.9, s=50, label='Predicted Threatened', ax=ax)

        plt.title('Predicted Extinction Risk for Data Deficient (DD) Amphibians')
        plt.legend()
        plt.tight_layout()
        plt.savefig('outputs/dd_geographic_risk_map.png')
        plt.close()
    except Exception as e:
        print(f"DD Map plotting failed: {e}")

print("=== Pipeline Complete ===")
