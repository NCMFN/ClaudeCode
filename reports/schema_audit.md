# Schema Audit Report

## Plant 1 Generation
- **Rows**: 68778
- **Date Range**: 01-06-2020 00:00 to 31-05-2020 23:45

### Column Details
- **DATE_TIME**: Dtype: `str`, Missing: 0.00%
- **PLANT_ID**: Dtype: `int64`, Missing: 0.00%
- **SOURCE_KEY**: Dtype: `str`, Missing: 0.00%
- **DC_POWER**: Dtype: `float64`, Missing: 0.00%
- **AC_POWER**: Dtype: `float64`, Missing: 0.00%
- **DAILY_YIELD**: Dtype: `float64`, Missing: 0.00%
- **TOTAL_YIELD**: Dtype: `float64`, Missing: 0.00%

## Plant 1 Weather
- **Rows**: 3182
- **Date Range**: 2020-05-15 00:00:00 to 2020-06-17 23:45:00

### Column Details
- **DATE_TIME**: Dtype: `str`, Missing: 0.00%
- **PLANT_ID**: Dtype: `int64`, Missing: 0.00%
- **SOURCE_KEY**: Dtype: `str`, Missing: 0.00%
- **AMBIENT_TEMPERATURE**: Dtype: `float64`, Missing: 0.00%
- **MODULE_TEMPERATURE**: Dtype: `float64`, Missing: 0.00%
- **IRRADIATION**: Dtype: `float64`, Missing: 0.00%

## Plant 2 Generation
- **Rows**: 67698
- **Date Range**: 2020-05-15 00:00:00 to 2020-06-17 23:45:00

### Column Details
- **DATE_TIME**: Dtype: `str`, Missing: 0.00%
- **PLANT_ID**: Dtype: `int64`, Missing: 0.00%
- **SOURCE_KEY**: Dtype: `str`, Missing: 0.00%
- **DC_POWER**: Dtype: `float64`, Missing: 0.00%
- **AC_POWER**: Dtype: `float64`, Missing: 0.00%
- **DAILY_YIELD**: Dtype: `float64`, Missing: 0.00%
- **TOTAL_YIELD**: Dtype: `float64`, Missing: 0.00%

## Plant 2 Weather
- **Rows**: 3259
- **Date Range**: 2020-05-15 00:00:00 to 2020-06-17 23:45:00

### Column Details
- **DATE_TIME**: Dtype: `str`, Missing: 0.00%
- **PLANT_ID**: Dtype: `int64`, Missing: 0.00%
- **SOURCE_KEY**: Dtype: `str`, Missing: 0.00%
- **AMBIENT_TEMPERATURE**: Dtype: `float64`, Missing: 0.00%
- **MODULE_TEMPERATURE**: Dtype: `float64`, Missing: 0.00%
- **IRRADIATION**: Dtype: `float64`, Missing: 0.00%

## Summary Statistics
### Plant 1 Generation
|       |      PLANT_ID |   DC_POWER |   AC_POWER |   DAILY_YIELD |      TOTAL_YIELD |
|:------|--------------:|-----------:|-----------:|--------------:|-----------------:|
| count | 68778         |   68778    | 68778      |      68778    |  68778           |
| mean  |     4.135e+06 |    3147.43 |   307.803  |       3295.97 |      6.97871e+06 |
| std   |     0         |    4036.46 |   394.396  |       3145.18 | 416272           |
| min   |     4.135e+06 |       0    |     0      |          0    |      6.18364e+06 |
| 25%   |     4.135e+06 |       0    |     0      |          0    |      6.512e+06   |
| 50%   |     4.135e+06 |     429    |    41.4938 |       2658.71 |      7.14668e+06 |
| 75%   |     4.135e+06 |    6366.96 |   623.619  |       6274    |      7.26871e+06 |
| max   |     4.135e+06 |   14471.1  |  1410.95   |       9163    |      7.84682e+06 |

### Plant 1 Weather
|       |     PLANT_ID |   AMBIENT_TEMPERATURE |   MODULE_TEMPERATURE |   IRRADIATION |
|:------|-------------:|----------------------:|---------------------:|--------------:|
| count | 3182         |            3182       |            3182      |  3182         |
| mean  |    4.135e+06 |              25.5316  |              31.091  |     0.228313  |
| std   |    0         |               3.35486 |              12.2612 |     0.300836  |
| min   |    4.135e+06 |              20.3985  |              18.1404 |     0         |
| 25%   |    4.135e+06 |              22.7052  |              21.0906 |     0         |
| 50%   |    4.135e+06 |              24.6138  |              24.6181 |     0.0246535 |
| 75%   |    4.135e+06 |              27.9205  |              41.3078 |     0.449588  |
| max   |    4.135e+06 |              35.2525  |              65.5457 |     1.22165   |

### Plant 2 Generation
|       |      PLANT_ID |   DC_POWER |   AC_POWER |   DAILY_YIELD |     TOTAL_YIELD |
|:------|--------------:|-----------:|-----------:|--------------:|----------------:|
| count | 67698         |  67698     |  67698     |      67698    | 67698           |
| mean  |     4.136e+06 |    246.702 |    241.278 |       3294.89 |     6.58945e+08 |
| std   |     0         |    370.57  |    362.112 |       2919.45 |     7.29668e+08 |
| min   |     4.136e+06 |      0     |      0     |          0    |     0           |
| 25%   |     4.136e+06 |      0     |      0     |        272.75 |     1.99649e+07 |
| 50%   |     4.136e+06 |      0     |      0     |       2911    |     2.82628e+08 |
| 75%   |     4.136e+06 |    446.592 |    438.215 |       5534    |     1.3485e+09  |
| max   |     4.136e+06 |   1420.93  |   1385.42  |       9873    |     2.24792e+09 |

### Plant 2 Weather
|       |     PLANT_ID |   AMBIENT_TEMPERATURE |   MODULE_TEMPERATURE |   IRRADIATION |
|:------|-------------:|----------------------:|---------------------:|--------------:|
| count | 3259         |            3259       |            3259      |  3259         |
| mean  |    4.136e+06 |              28.0694  |              32.7724 |     0.232737  |
| std   |    0         |               4.06156 |              11.344  |     0.312693  |
| min   |    4.136e+06 |              20.9424  |              20.2651 |     0         |
| 25%   |    4.136e+06 |              24.6021  |              23.7169 |     0         |
| 50%   |    4.136e+06 |              26.9813  |              27.5346 |     0.0190405 |
| 75%   |    4.136e+06 |              31.0568  |              40.4807 |     0.438717  |
| max   |    4.136e+06 |              39.1816  |              66.636  |     1.09877   |

## Data Characteristics
### Confirmed available fields
- Module Temperature
- Ambient Temperature
- DC Power
- AC Power

### Confirmed absent fields
- THD
- Frequency Deviation
- Reactive Power
- Fault/IGBT Labels
