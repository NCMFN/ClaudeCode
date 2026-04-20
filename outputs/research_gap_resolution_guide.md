# Complete Guide to Addressing Research Gaps
## Based on Uploaded Session 2 Pipeline

## Pipeline Summary (from uploaded file)
The current `pipeline.py` provides an end-to-end framework for modeling amphibian extinction risk.
- **Data ingestion:** Downloads AmphiBIO traits, WorldClim bioclimatic rasters, and AmphibiaWeb taxonomy dynamically. It then fetches GBIF occurrences and IUCN status.
- **Feature engineering:** Performs basic spatial point extraction for WorldClim rasters.
- **Range size computation:** Computes a highly simplified bounding box area `(max_lon - min_lon) * (max_lat - min_lat)`.
- **Model training & CV:** Preprocesses data with simple median imputation and standard scaling. Evaluates `XGBClassifier` utilizing `GroupKFold` with `KMeans` spatial clustering for ablation models.
- **DD Prediction logic:** Separates 'DATA_DEFICIENT' species and applies the trained Climate-Only model to generate provisional predictions, outputting risk ranking and geographic visualizations.

Despite these advanced steps, the pipeline contains hardcoded limits (e.g., `species_list[:1500]`, `limit=5` occurrences), simplistic spatial calculations, and lacks corrections for fundamental ecological biases.

---

## GAP 1: Scale limitations (species cap, GBIF occurrence limits)

**Why this matters**
A sample of 5 occurrences per species is vastly insufficient to capture the climatic envelope or true geographic extent of an amphibian, leading to severe underestimations of habitat variability. Furthermore, arbitrarily capping the dataset at 1,500 species prevents true global generalization and diminishes the statistical power required for deep learning or robust ensemble modeling.

**What the current code does**
The GBIF fetcher function explicitly caps occurrences at 5:
`occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=5"`
And limits the species queried to 1,500:
`subset = species_list[:1500]`

**What is wrong or missing**
The limits artificially restrict the model's spatial awareness. By severely truncating the data, the calculated mean climatic variables and spatial range estimates become highly skewed and unrepresentative of the species' true ecological niche.

**Exact code changes (drop-in ready)**

MODIFY THIS SECTION in `pipeline.py` (Phase 2):
```python
# REPLACE THIS:
# occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=5"
# occ_res = requests.get(occ_url, timeout=5).json()
# coords = [(r['decimalLongitude'], r['decimalLatitude']) for r in occ_res.get('results', []) if 'decimalLongitude' in r]

# ADD THIS:
# Increase the occurrence limit to 300 to better capture the ecological envelope
occ_url = f"https://api.gbif.org/v1/occurrence/search?taxonKey={usage_key}&hasCoordinate=true&limit=300"
occ_res = requests.get(occ_url, timeout=10).json()
coords = [(r['decimalLongitude'], r['decimalLatitude']) for r in occ_res.get('results', []) if 'decimalLongitude' in r]


# REPLACE THIS:
# print("Fetching GBIF data (Sampling 1500 for demonstration)...")
# subset = species_list[:1500]

# ADD THIS:
print("Fetching GBIF data (Processing the full globally validated species list)...")
subset = species_list # Removes the arbitrary 1500 cap
```

**Expected impact**
Greatly enhances the ecological validity of the climatic features and extends the pipeline's applicability to the entire known amphibian taxonomy, turning it into a true global analysis rather than a toy demonstration.

---

## GAP 2: Range size estimation flaws (bounding box vs ecological range)

**Why this matters**
Extinction risk is heavily correlated with Extent of Occurrence (EOO). The current pipeline calculates range size using a simple bounding box (`Delta Lon * Delta Lat`), which wildly overestimates range sizes for species with curved or non-rectangular distributions (e.g., coastal or mountain-range restricted species).

**What the current code does**
Calculates bounding box area trivially:
`climate_row["range_size_deg2"] = (max(lons) - min(lons)) * (max(lats) - min(lats)) if len(lons) > 1 else 0`

**What is wrong or missing**
This rectangular bounding box fails to account for the Earth's curvature (degrees are not equal area) and ignores the actual shape of the occurrence points. A Minimum Convex Polygon (Convex Hull) or Alpha Shape should be used.

**Exact code changes (drop-in ready)**

MODIFY THIS SECTION in `pipeline.py` (Phase 3):
```python
# ADD THIS (At the top of the file with other imports):
from shapely.geometry import MultiPoint

# REPLACE THIS:
# climate_row["range_size_deg2"] = (max(lons) - min(lons)) * (max(lats) - min(lats)) if len(lons) > 1 else 0

# ADD THIS:
if len(coords) >= 3:
    # Calculate the Minimum Convex Polygon (Convex Hull) area in pseudo-degrees
    mcp = MultiPoint(coords).convex_hull
    climate_row["range_size_deg2"] = mcp.area
elif len(coords) == 2:
    climate_row["range_size_deg2"] = MultiPoint(coords).length * 0.01 # minimal line buffer
else:
    climate_row["range_size_deg2"] = 0
```

**Expected impact**
Reduces the gross overestimation of range sizes, providing a much more accurate proxy for EOO. This directly improves the model's ability to identify narrow-range endemics, which are highly susceptible to extinction.

---

## GAP 3: Spatial autocorrelation / CV leakage

**Why this matters**
Spatial autocorrelation occurs when species located near each other share similar climates and traits. If a model is trained on species in a specific region and tested on species in the exact same region, performance metrics are artificially inflated (data leakage).

**What the current code does**
It applies `GroupKFold` using simple `KMeans` on `mean_lon` and `mean_lat`:
`spatial_groups = kmeans.fit_predict(df_assessed[['mean_lon', 'mean_lat']].fillna(0))`

**What is wrong or missing**
While clustering coordinates is a good start, KMeans strictly based on raw Lon/Lat distorts polar distances and ignores biogeographical barriers (like oceans or mountain ranges). Spatial cross-validation should ideally block by distinct Bioregions or explicitly use spatial distancing buffers, not unprojected KMeans.

**Exact code changes (drop-in ready)**

MODIFY THIS SECTION in `pipeline.py` (Phase 4):
```python
# REPLACE THIS:
# kmeans = KMeans(n_clusters=5, random_state=42)
# spatial_groups = kmeans.fit_predict(df_assessed[['mean_lon', 'mean_lat']].fillna(0))

# ADD THIS:
from sklearn.cluster import AgglomerativeClustering
# Convert lat/lon to approximate 3D Cartesian coordinates to handle Earth's curvature for clustering
lon_rad = np.radians(df_assessed['mean_lon'].fillna(0).values)
lat_rad = np.radians(df_assessed['mean_lat'].fillna(0).values)
x = np.cos(lat_rad) * np.cos(lon_rad)
y = np.cos(lat_rad) * np.sin(lon_rad)
z = np.sin(lat_rad)
cartesian_coords = np.column_stack((x, y, z))

# Use spatial agglomerative clustering with 10 distinct global biogeographic pseudo-regions
spatial_clusterer = AgglomerativeClustering(n_clusters=10, metric='euclidean', linkage='ward')
spatial_groups = spatial_clusterer.fit_predict(cartesian_coords)
```

**Expected impact**
Prevents spatial leakage across the poles or dateline and creates more ecologically cohesive validation folds. Evaluation metrics will reflect true spatial generalization, standardizing the methodology against rigorous macroecological studies.

---

## GAP 4: Assessor bias in IUCN labels

**Why this matters**
The IUCN Red List is evaluated by human experts. Assessments can be biased by taxonomic group, region, or the availability of funding, leading to inconsistent thresholds for "Threatened" classifications.

**What the current code does**
Directly maps IUCN text labels to binary targets without any adjustment for assessment year or regional assessment bias.

**What is wrong or missing**
The pipeline completely ignores the potential for label noise. While fully eliminating assessor bias is difficult, incorporating the taxonomic order or the primary geographic region as control features can allow the model to implicitly adjust for baseline assessment stringency across different amphibian lineages (e.g., Anura vs Caudata).

**Exact code changes (drop-in ready)**

MODIFY THIS SECTION in `pipeline.py` (Phase 4):
```python
# ADD THIS:
# Incorporate Taxonomic 'Order' from AmphiBIO to control for lineage-specific assessor bias
if 'Order' in df_assessed.columns:
    # One-hot encode the Order
    df_assessed = pd.get_dummies(df_assessed, columns=['Order'], drop_first=True)
    df_dd = pd.get_dummies(df_dd, columns=['Order'], drop_first=True)

    # Ensure DD has the same one-hot columns
    for col in df_assessed.columns:
        if col.startswith('Order_') and col not in df_dd.columns:
            df_dd[col] = 0

    # Add Order columns to the all_features list
    order_cols = [c for c in df_assessed.columns if c.startswith('Order_')]
    all_features.extend(order_cols)
```

**Expected impact**
Helps the model control for phylogenetic and taxonomic biases present in human assessments, ensuring that risk predictions are not artificially skewed by the over-representation of well-studied orders.

---

## GAP 5: Taxonomic stratification (Order-level differences)

**Why this matters**
Amphibians are divided into three distinct orders: Anura (frogs), Caudata (salamanders), and Gymnophiona (caecilians). These lineages have vastly different ecological requirements, dispersal capabilities, and threat responses.

**What the current code does**
Treats all amphibians as a single homogeneous group during modeling.

**What is wrong or missing**
By not providing the model with taxonomic hierarchy, it cannot learn interactions between climate vulnerability and specific evolutionary lineages.

**Exact code changes (drop-in ready)**
*(This is effectively resolved by the code block provided in GAP 4, which explicitly injects the `Order` taxonomy into the feature set via one-hot encoding.)*

**Expected impact**
Allows tree-based models to create interaction splits (e.g., "If Order is Caudata AND bio_1_mean > X -> High Risk"), capturing lineage-specific extinction drivers.

---

## GAP 6: Model performance on narrow-range species

**Why this matters**
Narrow-range endemics are inherently more likely to be threatened. Standard classification metrics (Accuracy, ROC-AUC) on the whole dataset can look excellent even if the model performs poorly on these specific, highly critical species, masking severe conservation blind spots.

**What the current code does**
Reports standard accuracy and ROC-AUC on the entire spatial holdout fold.

**What is wrong or missing**
There is no isolated evaluation of model performance on narrow-range species. If the model consistently misclassifies narrow-range species but gets wide-range species correct, it is useless for targeted conservation.

**Exact code changes (drop-in ready)**

ADD THIS SECTION in `pipeline.py` (Phase 5, after the cross-validation printouts):
```python
# ADD THIS:
# Evaluate specifically on Narrow-Range endemics (bottom 25% of range size)
narrow_range_threshold = np.percentile(df_assessed['range_size_deg2'].dropna(), 25)
narrow_mask = X_all_assessed[:, all_features.index('range_size_deg2')] <= narrow_range_threshold

if sum(narrow_mask) > 0:
    X_narrow = X_a_scaled[narrow_mask]
    y_narrow = y_assessed[narrow_mask]

    # Train model on all data, evaluate on narrow-range subset
    xgb_narrow = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    xgb_narrow.fit(X_a_scaled, y_assessed)

    narrow_preds = xgb_narrow.predict(X_narrow)
    if len(np.unique(y_narrow)) > 1:
        narrow_auc = roc_auc_score(y_narrow, xgb_narrow.predict_proba(X_narrow)[:, 1])
        print(f"-> Narrow-Range Species ROC-AUC: {narrow_auc:.4f}")
    print(f"-> Narrow-Range Species Accuracy: {accuracy_score(y_narrow, narrow_preds):.4f}")
```

**Expected impact**
Provides critical visibility into whether the model is actually learning the niche requirements of the most vulnerable species, validating its utility for prioritizing localized conservation efforts.

---

## GAP 7: DD prediction scale and uncertainty

**Why this matters**
Providing a point-estimate probability for Data Deficient species without quantifying the uncertainty or confidence of that prediction is scientifically hazardous. DD species might exist in climatic envelopes completely unseen during training.

**What the current code does**
Generates a single predicted probability using `xgb_climate.predict_proba()`.

**What is wrong or missing**
It fails to output an uncertainty metric or confidence interval.

**Exact code changes (drop-in ready)**

MODIFY THIS SECTION in `pipeline.py` (Phase 6):
```python
# REPLACE THIS:
# xgb_climate.fit(X_c_scaled, y_assessed)
# X_dd_scaled = scaler_climate.transform(X_climate_dd)
# dd_probs = xgb_climate.predict_proba(X_dd_scaled)[:, 1]

# ADD THIS:
# Use an ensemble of models (Bagging approach) to calculate prediction uncertainty (standard deviation)
n_iterations = 10
dd_prob_matrix = np.zeros((len(X_dd_scaled), n_iterations))

for i in range(n_iterations):
    # Train with different random seeds to simulate ensemble variance
    xgb_ensemble = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=i*42, subsample=0.8)
    xgb_ensemble.fit(X_c_scaled, y_assessed)
    dd_prob_matrix[:, i] = xgb_ensemble.predict_proba(X_dd_scaled)[:, 1]

# Calculate mean probability and standard deviation (uncertainty)
dd_probs = np.mean(dd_prob_matrix, axis=1)
dd_uncertainty = np.std(dd_prob_matrix, axis=1)

df_dd['Predicted_Risk_Probability'] = dd_probs
df_dd['Prediction_Uncertainty'] = dd_uncertainty
df_dd['Predicted_Threat_Status'] = ['Threatened' if p >= 0.5 else 'Non-Threatened' for p in dd_probs]

# Update the CSV export to include uncertainty
df_dd[['Species', 'Predicted_Risk_Probability', 'Prediction_Uncertainty', 'Predicted_Threat_Status']].sort_values(by='Predicted_Risk_Probability', ascending=False).to_csv('outputs/dd_provisional_predictions.csv', index=False)
```

**Expected impact**
Moves the output from a brittle point-estimate to a robust research-grade prediction, allowing conservationists to prioritize DD species that have both high threat probabilities and low model uncertainty.

---

## GAP 8: Pipeline staleness / lack of temporal updating

**Why this matters**
Extinction risks and GBIF occurrences are dynamic. A pipeline that hardcodes spatial limits and relies on static CSV extractions quickly becomes obsolete as taxonomy changes or new IUCN assessments are published.

**What the current code does**
Checks for the existence of `data/species_data_gbif.json` and skips fetching if it exists:
`if not os.path.exists('data/species_data_gbif.json'):`

**What is wrong or missing**
There is no mechanism to force an update or check the freshness of the cache. Running the pipeline months later will yield identical, stale results.

**Exact code changes (drop-in ready)**

MODIFY THIS SECTION in `pipeline.py` (Phase 2):
```python
# ADD THIS (At the top of the file):
import time

# REPLACE THIS:
# if not os.path.exists('data/species_data_gbif.json'):

# ADD THIS:
# Force refresh cache if it is older than 30 days
cache_file = 'data/species_data_gbif.json'
force_refresh = False

if os.path.exists(cache_file):
    file_age_days = (time.time() - os.path.getmtime(cache_file)) / (60*60*24)
    if file_age_days > 30:
        print("Cache is older than 30 days. Forcing GBIF data refresh...")
        force_refresh = True

if not os.path.exists(cache_file) or force_refresh:
```

**Expected impact**
Ensures the pipeline is a "living" framework that dynamically aligns with the latest ecological realities, aligning with the definition of an automated, API-native methodology.

---

## Implementation Priority Order
- **Phase 1 (Critical fixes):** GAP 1 (Scale limitations), GAP 2 (Range size flaws). These fundamentally alter the validity of the data flowing into the models.
- **Phase 2 (Methodological robustness):** GAP 3 (Spatial autocorrelation CV), GAP 4 & 5 (Assessor bias / Taxonomic stratification). These ensure the model learns true ecological constraints rather than human artifacts.
- **Phase 3 (Research contributions):** GAP 7 (DD Prediction uncertainty), GAP 6 (Narrow-range evaluation), GAP 8 (Temporal updating). These push the pipeline into the realm of novel, publishable research.
