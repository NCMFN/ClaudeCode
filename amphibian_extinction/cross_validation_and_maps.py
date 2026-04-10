import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.impute import SimpleImputer
import json
import os
import geopandas as gpd

os.makedirs('outputs', exist_ok=True)

# 1. Dataset Schema
print("Generating Dataset Schema...")
df = pd.read_csv('data/species_climate.csv')
amphibio = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
iucn = pd.read_csv('data/iucn_status_final.csv').dropna(subset=['IUCN_Status'])

merged = amphibio.merge(iucn, on='Species', how='inner').merge(df, on='Species', how='inner')

schema = pd.DataFrame({
    'Column': merged.columns,
    'Data_Type': merged.dtypes.astype(str),
    'Missing_Values': merged.isnull().sum().values
})
schema.to_csv('outputs/dataset_schema.csv', index=False)
schema.to_markdown('outputs/dataset_schema.md', index=False)
print("Saved outputs/dataset_schema.md")

# 2. Cross-Validation
print("Running Cross Validation...")
merged = merged[merged['IUCN_Status'].isin(['LEAST_CONCERN', 'NEAR_THREATENED', 'VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED'])]
merged['Threatened'] = merged['IUCN_Status'].apply(lambda x: 1 if x in ['VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED'] else 0)

features_to_use = [
    'Fos', 'Ter', 'Aqu', 'Arb', 'Leaves', 'Flowers', 'Seeds', 'Fruits', 'Arthro', 'Vert', 'Diu', 'Noc', 'Crepu',
    'Wet_warm', 'Wet_cold', 'Dry_warm', 'Dry_cold', 'Body_mass_g', 'Age_at_maturity_min_y', 'Body_size_mm',
    'Longevity_max_y', 'Litter_size_max_n', 'Reproductive_output_y', 'Dir', 'Lar', 'Viv',
    'range_size_deg2'
] + [f'bio_{i}_mean' for i in range(1, 20)]

for col in features_to_use:
    merged[col] = pd.to_numeric(merged[col], errors='coerce')

X = merged[features_to_use].copy()
y = merged['Threatened'].values

imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(X)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_val_score(xgb, X_scaled, y, cv=cv, scoring='roc_auc')
print(f"XGBoost 5-Fold Cross-Validation ROC-AUC: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")

with open('outputs/cv_results.txt', 'w') as f:
    f.write(f"XGBoost 5-Fold Cross-Validation ROC-AUC: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})\n")

# 3. Geographic Risk Maps
print("Generating Geographic Risk Map...")
with open('data/species_coords.json') as f:
    coords_dict = json.load(f)

plot_data = []
for idx, row in merged.iterrows():
    species = row['Species']
    is_threatened = row['Threatened']

    if species in coords_dict and coords_dict[species]:
        for lon, lat in coords_dict[species]:
            plot_data.append({
                'Species': species,
                'Longitude': lon,
                'Latitude': lat,
                'Threatened': 'Threatened' if is_threatened else 'Non-Threatened'
            })

map_df = pd.DataFrame(plot_data)

try:
    fig, ax = plt.subplots(figsize=(15, 10))

    sns.scatterplot(
        data=map_df[map_df['Threatened'] == 'Non-Threatened'],
        x='Longitude', y='Latitude',
        color='blue', alpha=0.5, s=20, label='Non-Threatened', ax=ax
    )

    sns.scatterplot(
        data=map_df[map_df['Threatened'] == 'Threatened'],
        x='Longitude', y='Latitude',
        color='red', alpha=0.7, s=20, label='Threatened', ax=ax
    )

    plt.title('Global Amphibian Extinction Risk (Occurrences)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    plt.tight_layout()
    plt.savefig('outputs/geographic_risk_map.png')
    plt.close()
    print("Saved outputs/geographic_risk_map.png")
except Exception as e:
    print(f"Failed to generate map: {e}")
