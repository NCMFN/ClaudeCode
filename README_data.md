# Downloaded Datasets

Per the prompt instructions to "provide the above datasets so that i can download it in .csv formats", I have processed all the links according to the data handling protocol.

1. **NEON Science Ticks & Data Products**
   - `data/neon_ticks.csv`: Pulled from the NEON Data API for product DP1.10092.001.

2. **GBIF Species**
   - `data/gbif_species_2190124.csv`: Pulled JSON payload from the GBIF API for taxonKey 2190124 and converted to CSV.

3. **NASA POWER**
   - `data/nasa_power.csv`: Downloaded hourly data for T2M using the NASA POWER API.

4. **Restricted/Broken Links:**
   - **GBIF IPT (neon-tick-abundance-diversity-pathogen-data)**: This resource returns an HTTP 404. Details are in `data/neon_tick_abundance_diversity_pathogen_status.txt`.
   - **USGS LPDAAC (mod13a3v061, gedi02_bv002) and NSIDC (spl3smp)**: These are landing pages for datasets requiring Earthdata Login for direct data downloads (HDF5/NetCDF). Under the strict "No Simulations" protocol, I cannot mock these files. I have instead saved their HTTP response status codes and scraped their landing page text to provide metadata CSVs (`data/mod13a3v061_metadata.csv`, `data/gedi02_bv002_metadata.csv`, `data/spl3smp_metadata.csv`).
