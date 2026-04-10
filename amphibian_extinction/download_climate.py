# Using WorldClim data or CHELSA: we just need some bioclimatic variables per species.
# To do this correctly:
# 1. We need species occurrences (GBIF).
# 2. Extract raster values at those points.
# Since getting millions of occurrences for 4800 species and running raster extraction takes days,
# memory says: "When specific datasets are requested, prioritize downloading them directly from their source websites using Python scripts. Only generate robust mock data if datasets are completely inaccessible and no other option exists, avoiding code placeholders."
# We can download a small sample of occurrence data for each species via GBIF API to get lat/lon,
# then use pybioclim or rasterio to sample WorldClim.
# WorldClim is ~1GB.
# For simplicity, since the prompt says "no simulation", we will:
# 1. Download WorldClim at lowest resolution (10m = 10 arc-minutes).
# 2. Fetch 10 occurrence points per species from GBIF.
# 3. Average the climate variables for those points.
pass
