# Classifying Historical Telegraph Defects

This repository contains the code and synthetic data generator for the HISTELCON conference paper on 19th-century submarine cable telemetry.

## Usage
Run the entire pipeline:
```bash
python run_pipeline.py
```

This will generate the synthetic data in `data/`, train models via `src/`, output plots to `figures/`, and write the paper draft to `paper/`.

## Data
Please see `data/DATA_CARD.md` for explicit documentation on the synthetic nature of this dataset and its historical grounding.
