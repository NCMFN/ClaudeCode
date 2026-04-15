"""
End-to-End Amphibian Extinction Risk Modelling Pipeline
Integrates:
1. AmphiBIO (Ecological Traits)
2. GBIF (Occurrences & IUCN Status)
3. WorldClim (Bioclimatic variables)
4. AmphibiaWeb (Taxonomy Validation)
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

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score, confusion_matrix, roc_curve
from sklearn.impute import SimpleImputer
import geopandas as gpd

# Suppress warnings for clean output
import warnings
warnings.filterwarnings('ignore')

os.makedirs('data', exist_ok=True)
os.makedirs('outputs', exist_ok=True)

# ---------------------------------------------------------
# 1. DATA ACQUISITION
# ---------------------------------------------------------
print("=== Phase 1: Data Acquisition ===")

# A. AmphiBIO
if not os.path.exists('data/AmphiBIO_v1.csv'):
    print("Downloading AmphiBIO...")
    url = "https://ndownloader.figshare.com/files/8828578"
    urllib.request.urlretrieve(url, 'data/AmphiBIO_v1.csv')

# B. WorldClim
if not os.path.exists('data/wc2.1_10m_bio/wc2.1_10m_bio_1.tif'):
    print("Downloading WorldClim (this may take a minute)...")
    url = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip"
    try:
        urllib.request.urlretrieve(url, 'data/wc2.1_10m_bio.zip')
        with zipfile.ZipFile('data/wc2.1_10m_bio.zip', 'r') as zip_ref:
            zip_ref.extractall('data/wc2.1_10m_bio')
    except Exception as e:
        print(f"Failed to download WorldClim: {e}")

# C. AmphibiaWeb
if not os.path.exists('data/amphibiaweb.txt'):
    print("Downloading AmphibiaWeb Taxonomy...")
    url = "https://amphibiaweb.org/amphib_names.txt"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            with open('data/amphibiaweb.txt', 'wb') as f:
                f.write(res.content)
    except Exception as e:
        print(f"Failed to fetch AmphibiaWeb (Network Issue): {e}")

# Load AmphiBIO
amphibio = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
species_list = amphibio['Species'].dropna().unique()
print(f"Found {len(species_list)} unique species in AmphiBIO.")

# Validate with AmphibiaWeb
print("Validating species taxonomy using AmphibiaWeb...")
if os.path.exists('data/amphibiaweb.txt'):
    df_aw = pd.read_csv('data/amphibiaweb.txt', sep='\t', on_bad_lines='skip')
    aw_species = set((df_aw['genus'].astype(str) + " " + df_aw['species'].astype(str)).tolist())
    validated_species = [s for s in species_list if s in aw_species]
    print(f"Successfully validated {len(validated_species)} species in AmphibiaWeb.")
    if len(validated_species) > 500:
        species_list = validated_species
else:
    print("AmphibiaWeb validation skipped due to missing data.")

# ---------------------------------------------------------
# 2. GBIF API QUERIES (IUCN Status + Occurrences)
# ---------------------------------------------------------
print("=== Phase 2: GBIF API & Feature Extraction ===")

def fetch_gbif_data(species_name):
    """Fetch IUCN status and 5 occurrence points per species"""
    try:
        url = f"https://api.gbif.org/v1/species/match?name={species_name}&class=Amphibia"
        res = requests.get(url, timeout=5).json()
        if 'usageKey' not in res:
            return None

        usage_key = res['usageKey']

        status = None
        # Get IUCN Status from species profile
        prof_url = f"https://api.gbif.org/v1/species/{usage_key}/distributions"
        prof_res = requests.get(prof_url, timeout=5).json()
        for d in prof_res.get('results', []):
            if 'threatStatus' in d:
                status = d['threatStatus']
                break

        # Get Occurrences
        occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=5"
        occ_res = requests.get(occ_url, timeout=5).json()
        coords = [(r['decimalLongitude'], r['decimalLatitude']) for r in occ_res.get('results', []) if 'decimalLongitude' in r]

        return {"Species": species_name, "IUCN_Status": status, "coords": coords}
    except:
        return None

if not os.path.exists('data/species_data_gbif.json'):
    print("Fetching GBIF data (Limiting to 1500 species to ensure fast execution)...")
    subset = species_list[:1500]
    gbif_results = []

    with ThreadPoolExecutor(max_workers=30) as executor:
        for i, res in enumerate(executor.map(fetch_gbif_data, subset)):
            if res and res["IUCN_Status"]:
                gbif_results.append(res)
            if (i+1) % 500 == 0:
                print(f"Processed {i+1}/{len(subset)}")

    with open('data/species_data_gbif.json', 'w') as f:
        json.dump(gbif_results, f)
else:
    print("Loading existing GBIF data...")
    with open('data/species_data_gbif.json') as f:
        gbif_results = json.load(f)

print(f"Acquired complete empirical GBIF data for {len(gbif_results)} species.")
if len(gbif_results) == 0:
    print("No GBIF data found. Pipeline cannot continue.")
    exit(1)

# ---------------------------------------------------------
# 3. RASTER EXTRACTION (WorldClim)
# ---------------------------------------------------------
print("=== Phase 3: Spatial Raster Extraction ===")

if not os.path.exists('data/species_climate.csv'):
    print("Extracting bioclimatic variables...")
    rasters = {}
    for i in range(1, 20):
        try:
            rasters[f"bio_{i}"] = rasterio.open(f"data/wc2.1_10m_bio/wc2.1_10m_bio_{i}.tif")
        except:
            pass

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
                    if val != src.nodata:
                        vals.append(val)
                except:
                    pass
            climate_row[f"{var}_mean"] = np.mean(vals) if vals else np.nan

        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        climate_row["range_size_deg2"] = (max(lons) - min(lons)) * (max(lats) - min(lats)) if len(lons) > 1 else 0
        climate_data.append(climate_row)

    df_climate = pd.DataFrame(climate_data)
    df_climate.to_csv('data/species_climate.csv', index=False)

    for src in rasters.values():
        src.close()
else:
    df_climate = pd.read_csv('data/species_climate.csv')

# ---------------------------------------------------------
# 4. DATA INTEGRATION & PREPROCESSING
# ---------------------------------------------------------
print("=== Phase 4: Data Integration & ML Preprocessing ===")

df = amphibio.merge(df_climate, on='Species', how='inner')

if df.empty or 'IUCN_Status' not in df.columns:
    print("Failed to merge datasets or missing IUCN_Status. Aborting.")
    exit(1)

# Target Definition
df = df[df['IUCN_Status'].isin(['LEAST_CONCERN', 'NEAR_THREATENED', 'VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED'])]
df['Threatened'] = df['IUCN_Status'].apply(lambda x: 1 if x in ['VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED'] else 0)

try:
    schema = pd.DataFrame({'Column': df.columns, 'Data_Type': df.dtypes.astype(str), 'Missing_Values': df.isnull().sum().values})
    schema.to_markdown('outputs/dataset_schema.md', index=False)
except:
    pass

traits = ['Fos', 'Ter', 'Aqu', 'Arb', 'Leaves', 'Flowers', 'Seeds', 'Fruits', 'Arthro', 'Vert', 'Diu', 'Noc', 'Crepu',
          'Wet_warm', 'Wet_cold', 'Dry_warm', 'Dry_cold', 'Body_mass_g', 'Age_at_maturity_min_y', 'Body_size_mm',
          'Longevity_max_y', 'Litter_size_max_n', 'Reproductive_output_y', 'Dir', 'Lar', 'Viv']
climate_features = [f'bio_{i}_mean' for i in range(1, 20)]
features_to_use = traits + ['range_size_deg2'] + climate_features

for col in features_to_use:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

actual_features = [f for f in features_to_use if f in df.columns]
X = df[actual_features].copy()
y = df['Threatened'].values

imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(X)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

try:
    from imblearn.over_sampling import SMOTE
    if sum(y==1) > 5 and sum(y==0) > 5:
        smote = SMOTE(random_state=42)
        X_res, y_res = smote.fit_resample(X_scaled, y)
    else:
        X_res, y_res = X_scaled, y
except:
    X_res, y_res = X_scaled, y

if len(y_res) > 20:
    X_train, X_test, y_train, y_test = train_test_split(X_res, y_res, test_size=0.2, random_state=42, stratify=y_res)
else:
    print("Not enough data to train models.")
    exit(1)

# ---------------------------------------------------------
# 5. MODELLING & EVALUATION
# ---------------------------------------------------------
print("=== Phase 5: Machine Learning Models ===")

xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)

try:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(xgb, X_train, y_train, cv=cv, scoring='roc_auc')
    print(f"XGBoost 5-Fold Cross-Validation ROC-AUC: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
except:
    pass

xgb.fit(X_train, y_train)
y_pred_xgb = xgb.predict(X_test)
y_prob_xgb = xgb.predict_proba(X_test)[:, 1]

print("XGBoost Test Accuracy:", accuracy_score(y_test, y_pred_xgb))
try:
    print("XGBoost Test ROC-AUC:", roc_auc_score(y_test, y_prob_xgb))
except:
    pass

# Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_prob_rf = rf.predict_proba(X_test)[:, 1]

# Deep Neural Network
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping

    nn = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])
    nn.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    nn.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2, callbacks=[early_stop], verbose=0)
    nn.save('outputs/amphibian_nn_model.keras')
except:
    pass

import joblib
joblib.dump(xgb, 'outputs/xgboost_model.pkl')

# ---------------------------------------------------------
# 6. VISUALIZATIONS
# ---------------------------------------------------------
print("=== Phase 6: Generating Figures ===")

try:
    fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)
    fpr_xgb, tpr_xgb, _ = roc_curve(y_test, y_prob_xgb)
    plt.figure(figsize=(8,6))
    plt.plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC = {roc_auc_score(y_test, y_prob_rf):.2f})')
    plt.plot(fpr_xgb, tpr_xgb, label=f'XGBoost (AUC = {roc_auc_score(y_test, y_prob_xgb):.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves')
    plt.legend()
    plt.tight_layout()
    plt.savefig('outputs/roc_curves.png')
    plt.close()
except:
    pass

cm = confusion_matrix(y_test, y_pred_xgb)
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Non-Threatened', 'Threatened'], yticklabels=['Non-Threatened', 'Threatened'])
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix - XGBoost')
plt.tight_layout()
plt.savefig('outputs/confusion_matrix.png')
plt.close()

importances = xgb.feature_importances_
indices = np.argsort(importances)[::-1]
top_n = min(15, len(actual_features))
plt.figure(figsize=(10, 6))
plt.title('Top Feature Importances (XGBoost)')
plt.bar(range(top_n), importances[indices][:top_n], align="center")
plt.xticks(range(top_n), [actual_features[i] for i in indices][:top_n], rotation=45, ha='right')
plt.tight_layout()
plt.savefig('outputs/feature_importance.png')
plt.close()

print("Generating Geographic Risk Map...")
plot_data = []
for item in gbif_results:
    if item["IUCN_Status"] in ['VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED']:
        t = 'Threatened'
    elif item["IUCN_Status"] in ['LEAST_CONCERN', 'NEAR_THREATENED']:
        t = 'Non-Threatened'
    else:
        continue

    if item.get("coords"):
        lon, lat = item["coords"][0]
        plot_data.append({'Longitude': lon, 'Latitude': lat, 'Threatened': t})

if plot_data:
    map_df = pd.DataFrame(plot_data)
    try:
        from urllib.request import urlretrieve
        urlretrieve("https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip", "data/ne_110m.zip")
        world = gpd.read_file('zip://data/ne_110m.zip')

        fig, ax = plt.subplots(figsize=(15, 10))
        world.boundary.plot(ax=ax, linewidth=1, color='black')

        sns.scatterplot(data=map_df[map_df['Threatened'] == 'Non-Threatened'], x='Longitude', y='Latitude', color='blue', alpha=0.5, s=20, label='Non-Threatened', ax=ax)
        sns.scatterplot(data=map_df[map_df['Threatened'] == 'Threatened'], x='Longitude', y='Latitude', color='red', alpha=0.7, s=20, label='Threatened', ax=ax)

        plt.title('Global Amphibian Extinction Risk (Occurrences)')
        plt.legend()
        plt.tight_layout()
        plt.savefig('outputs/geographic_risk_map.png')
        plt.close()
    except Exception as e:
        print(f"Map plotting failed: {e}")

print("=== Pipeline Complete ===")
