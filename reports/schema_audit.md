# Data Schema Audit

## Overall Statistics
### plant1_gen
- Rows: 68778
- Columns: 7
- Date Range: 2020-01-06 00:00:00 to 2020-12-06 23:45:00

### plant1_weather
- Rows: 3182
- Columns: 6
- Date Range: 2020-05-15 00:00:00 to 2020-06-17 23:45:00

### plant2_gen
- Rows: 67698
- Columns: 7
- Date Range: 2020-05-15 00:00:00 to 2020-06-17 23:45:00

### plant2_weather
- Rows: 3259
- Columns: 6
- Date Range: 2020-05-15 00:00:00 to 2020-06-17 23:45:00

## Confirmed Available Fields
- heatsink/module temperature (MODULE_TEMPERATURE), ambient temperature (AMBIENT_TEMPERATURE), DC power (DC_POWER), AC power (AC_POWER)

## Confirmed Absent Fields
Based on the column schemas in the loaded datasets, the following required fields are **absent** from the real data:
- Total Harmonic Distortion (THD)
- Frequency deviation (Δf)
- Reactive power
- IGBT/fault event labels (true ground truth fault states)
