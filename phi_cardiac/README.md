# Pollution-Heat Index: Predicting Cardiac Stress During Extreme Heat Waves

This project develops a unified "Pollution-Heat Index" (PHI) to predict daily cardiac ER admissions using synergistic environmental regression models.

## Structure
- `data/raw/`: Raw downloaded (or simulated) datasets
- `data/processed/`: Aligned and featured datasets
- `src/`: Python source files for the ETL and ML pipeline
- `notebooks/`: Exploratory Data Analysis notebooks
- `outputs/`: Trained models, figures, and metrics

## API Setup Instructions

### OpenAQ v3
To use real data from OpenAQ, register at [OpenAQ Platform](https://openaq.org/developers/platform-overview/) and acquire an API key.
Place it in your environment:
```bash
export OPENAQ_API_KEY="your-key-here"
```

### Copernicus CDS (ERA5 Data)
To download ERA5 data:
1. Register an account at [Copernicus CDS](https://cds.climate.copernicus.eu/).
2. Agree to the Terms of Use.
3. Obtain your API key and save it to `~/.cdsapirc`:
```
url: https://cds.climate.copernicus.eu/api/v2
key: UID:API-KEY
```

### Cardiac Events Data
The original study targets PhysioNet MIMIC-IV ED data. Access requires free credentialing at [PhysioNet](https://physionet.org/content/mimic-iv-ed/2.2/).
For demonstration purposes in this repository, synthetic cardiac event data is generated matching the statistical distribution.

## Running the Pipeline

1. **Fetch Data:**
   ```bash
   python src/fetch_openaq.py
   python src/fetch_era5.py
   python src/fetch_health.py
   ```

2. **Align and Feature Engineering:**
   ```bash
   python src/align.py
   python src/features.py
   ```

3. **Train Models:**
   ```bash
   python src/train.py
   ```

4. **Evaluate:**
   ```bash
   python src/evaluate.py
   ```
