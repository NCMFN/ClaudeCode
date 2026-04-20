# Real-World Biodiversity and Conservation Analysis

## 1. Summary of Findings
- **Global Distribution:** Amphibian occurrences are heavily clustered in regions with dense research coverage or known biodiversity hotspots (e.g., South America, parts of Europe and Australia).
- **Conservation Status:** Analysis of the random sample from AmphiBIO mapped to GBIF indicates that while the majority of recorded occurrences belong to 'Least Concern' (LC) species, a significant portion falls under 'Vulnerable' (VU), 'Endangered' (EN), and 'Near Threatened' (NT).
- **Data Gaps:**
  - *IUCN API Limitation:* The official IUCN Red List API returned 404/access issues, necessitating the extraction of IUCN status via the GBIF backbone taxonomy API as a reliable proxy.
  - *Geographic Gaps:* Many AmphiBIO records lack associated high-resolution coordinate data in GBIF, reducing the total mappable occurrences.
- **Cross-dataset Consistency:** Some taxonomy mismatches occur between AmphiBIO's older taxonomy and GBIF's current backbone, handled by resolving names via the GBIF species match API.

## 2. Data Processing Steps
1. **Data Ingestion:**
   - Downloaded the **AmphiBIO v1** dataset directly from Figshare using `wget` to ensure programmatic reproducibility without 403 errors.
   - Queried the **GBIF API** (Species Match and Occurrence Search) to dynamically retrieve geographic coordinates, taxonomy, and conservation status for the species.
2. **Data Cleaning:**
   - Filtered out records with missing geographic coordinates (`decimalLatitude`, `decimalLongitude`).
   - Addressed taxonomy mismatches by matching AmphiBIO species names against the GBIF backbone taxonomy to retrieve the accepted `usageKey`.
3. **Data Merging:**
   - Merged the cleaned GBIF occurrences with AmphiBIO metadata (Order, Family, Body Size) using a Left Join on the scientific species name to prevent target leakage and data fabrication.

## 3. Visualizations
The analysis generated the following visualizations:
1. **`global_species_map.png`**: A geographic point map displaying global species occurrences, color-coded by their IUCN conservation status. This highlights spatial distributions of threatened vs. least concern species.
2. **`conservation_status_bar.png`**: A bar chart quantifying the total occurrence records grouped by their IUCN status.
3. **`species_density_heatmap.png`**: A spatial density heatmap using Seaborn's `kdeplot` over a world map to identify geographic biodiversity hotspots where occurrence records are most dense.
4. **`temporal_trends_timeseries.png`**: A histogram showing the frequency of species occurrence records collected over time (from 1970 to present), indicating temporal reporting trends.
5. **`system_architecture.png`**: A programmatic architecture diagram depicting the flow of data from external APIs/datasets through the ETL, Storage, Analysis, and Visualization layers.

## 4. System Architecture
A standard ETL and Analysis pipeline:
- **Data Sources:** External APIs (GBIF) and direct downloads (Figshare for AmphiBIO).
- **Ingestion:** Python `requests` and shell commands (`wget`) pull the raw data.
- **Processing (ETL):** `pandas` cleans coordinates, resolves taxonomy, and merges the datasets.
- **Storage:** Cleaned and merged data is stored as local CSVs and in-memory `GeoDataFrames`.
- **Analysis:** Cross-dataset consistency checks, taxonomy matching, and conservation status aggregation.
- **Visualization:** Maps and charts generated using `matplotlib`, `seaborn`, and `geopandas`.
