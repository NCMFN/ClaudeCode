# Dementia Geospatial Risk Analysis

This project builds an end-to-end ML pipeline that integrates CDC health surveillance data, NOAA solar/climate records, and EPA air quality metrics to train an ensemble classifier for tri-level dementia environmental risk classification across US counties.

## Log of Data Download Steps
- `LLCP2022XPT.zip` (CDC BRFSS): Downloaded 80.6 MB, extracted to `LLCP2022.XPT`
- `annual_conc_by_monitor_2022.zip` (EPA PM2.5): Downloaded 3.8 MB, extracted CSV
- `tl_2022_us_county.zip` (Census Shapefiles): Downloaded 79.4 MB, extracted SHP
