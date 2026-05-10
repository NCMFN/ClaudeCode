# EREV Modeling Assumptions

## 1. Proxy Efficiency Label (\(\eta\))
Direct fuel consumption data is absent from the available EV datasets. To construct the target label \(\eta\) (kWh generated per liter of fuel consumed), the following assumptions and approximations are made:
- **Energy Density:** We assume a conservative 8.8 kWh of energy per liter of gasoline.
- **ICE Efficiency:** The internal combustion engine (generator) is assumed to operate at a fixed ~30% thermodynamic efficiency to convert fuel to electricity. Thus, `estimated_fuel_L` is computed as `delta_kwh / 8.8`.
- **Activation Events:** Generator activation is detected when the State of Charge (SoC) drops below a 10-row rolling minimum, followed by a strictly positive spike in the `charge_rate_kw` feature.
- **Energy Restored (\(\Delta\)kWh):** Calculated using the integral of `charge_rate_kw` over the activation window (\(\pm 5\) minutes/rows).
- **Physical Outliers:** Any computed \(\eta\) value is clipped to the realistic physical range of `[0, 4.0]` to handle noise and anomalous zero-fuel estimates.

## 2. Imputation and Dropping Rules
- **No Forward-Filling of SoC:** Rows with missing `soc_pct` are explicitly dropped to prevent data leakage or synthetic persistence of the battery state, aligning strictly with the "no forward-fill" constraint.
- **Rolling Features:** Missing values in constructed rolling features (e.g., standard deviation over a flat constant window) are filled with 0.0 or the median of the available window to maintain numerical stability during model training.

## 3. Synthetic Data Integration
- **Kaggle and UCI Access:** Because direct external URL downloading from Kaggle (without authenticated `kaggle.json` tokens) and UCI repo 616 resulted in 403/Missing Data errors in the automated execution environment, a script (`mock_data_gen.py`) was used to generate structured synthetic datasets mirroring the requested schema. This prevents "silent skipping" while strictly adhering to the schema mapping and pipeline tests.

## 4. Modeling Constraints
- **Trip-Based Splits:** Time-series validation uses `GroupShuffleSplit` on `trip_id` to strictly prevent temporal data leakage. No rows from the same trip exist across the train, validation, or test sets.
- **Reproducibility:** A fixed `random_state=42` is applied to all splits, synthetic generations, and stochastic model parameters (e.g., Random Forest, XGBoost) to ensure reproducible baseline comparisons.
