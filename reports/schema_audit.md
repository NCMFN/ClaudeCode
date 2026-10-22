# Schema Audit Report

## Plant_1_Generation_Data.csv

- **Row count**: 68778
- **Date range**: 2020-05-15 00:00:00 to 2020-06-17 23:45:00

### Columns
| Column Name | Data Type | Missing Values (%) | Summary Statistics |
|-------------|-----------|--------------------|--------------------|
| DATE_TIME | datetime64[us] | 0.00% | unique: 3158 |
| PLANT_ID | int64 | 0.00% | min: 4135001.00, max: 4135001.00, mean: 4135001.00 |
| SOURCE_KEY | str | 0.00% | unique: 22 |
| DC_POWER | float64 | 0.00% | min: 0.00, max: 14471.12, mean: 3147.43 |
| AC_POWER | float64 | 0.00% | min: 0.00, max: 1410.95, mean: 307.80 |
| DAILY_YIELD | float64 | 0.00% | min: 0.00, max: 9163.00, mean: 3295.97 |
| TOTAL_YIELD | float64 | 0.00% | min: 6183645.00, max: 7846821.00, mean: 6978711.76 |

## Plant_1_Weather_Sensor_Data.csv

- **Row count**: 3182
- **Date range**: 2020-01-06 00:00:00 to 2020-12-06 23:45:00

### Columns
| Column Name | Data Type | Missing Values (%) | Summary Statistics |
|-------------|-----------|--------------------|--------------------|
| DATE_TIME | datetime64[us] | 0.00% | unique: 3182 |
| PLANT_ID | int64 | 0.00% | min: 4135001.00, max: 4135001.00, mean: 4135001.00 |
| SOURCE_KEY | str | 0.00% | unique: 1 |
| AMBIENT_TEMPERATURE | float64 | 0.00% | min: 20.40, max: 35.25, mean: 25.53 |
| MODULE_TEMPERATURE | float64 | 0.00% | min: 18.14, max: 65.55, mean: 31.09 |
| IRRADIATION | float64 | 0.00% | min: 0.00, max: 1.22, mean: 0.23 |

## Plant_2_Generation_Data.csv

- **Row count**: 67698
- **Date range**: 2020-01-06 00:00:00 to 2020-12-06 23:45:00

### Columns
| Column Name | Data Type | Missing Values (%) | Summary Statistics |
|-------------|-----------|--------------------|--------------------|
| DATE_TIME | datetime64[us] | 0.00% | unique: 3259 |
| PLANT_ID | int64 | 0.00% | min: 4136001.00, max: 4136001.00, mean: 4136001.00 |
| SOURCE_KEY | str | 0.00% | unique: 22 |
| DC_POWER | float64 | 0.00% | min: 0.00, max: 1420.93, mean: 246.70 |
| AC_POWER | float64 | 0.00% | min: 0.00, max: 1385.42, mean: 241.28 |
| DAILY_YIELD | float64 | 0.00% | min: 0.00, max: 9873.00, mean: 3294.89 |
| TOTAL_YIELD | float64 | 0.00% | min: 0.00, max: 2247916295.00, mean: 658944788.42 |

## Plant_2_Weather_Sensor_Data.csv

- **Row count**: 3259
- **Date range**: 2020-01-06 00:00:00 to 2020-12-06 23:45:00

### Columns
| Column Name | Data Type | Missing Values (%) | Summary Statistics |
|-------------|-----------|--------------------|--------------------|
| DATE_TIME | datetime64[us] | 0.00% | unique: 3259 |
| PLANT_ID | int64 | 0.00% | min: 4136001.00, max: 4136001.00, mean: 4136001.00 |
| SOURCE_KEY | str | 0.00% | unique: 1 |
| AMBIENT_TEMPERATURE | float64 | 0.00% | min: 20.94, max: 39.18, mean: 28.07 |
| MODULE_TEMPERATURE | float64 | 0.00% | min: 20.27, max: 66.64, mean: 32.77 |
| IRRADIATION | float64 | 0.00% | min: 0.00, max: 1.10, mean: 0.23 |

## Data Characteristics

### Confirmed available fields
- MODULE_TEMPERATURE (heatsink/module temperature)
- AMBIENT_TEMPERATURE (ambient temperature)

### Confirmed absent fields
- THD (Total Harmonic Distortion)
- Frequency deviation
- Reactive power
- IGBT/fault event labels
