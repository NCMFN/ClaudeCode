import nbformat as nbf
import os

with open('Flight_Delay_Prediction.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

preprocessing_eda_cell = nbf.v4.new_code_cell('''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# --- 1. Load Data ---
print("Loading Flight Data...")
flights_file = "data/On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2023_1.csv"
# Only load a subset of columns to save memory
cols_to_use = ['FlightDate', 'Reporting_Airline', 'Origin', 'Dest', 'CRSDepTime', 'DepTime', 'DepDelay',
               'TaxiOut', 'WheelsOff', 'WheelsOn', 'TaxiIn', 'CRSArrTime', 'ArrTime', 'ArrDelay',
               'Cancelled', 'CancellationCode', 'Diverted', 'CRSElapsedTime', 'ActualElapsedTime', 'Distance']

flights_df = pd.read_csv(flights_file, usecols=cols_to_use)
# Keep only top 5 busiest airports for origin and destination to manage memory and simplify
top_airports = ['ORD', 'ATL', 'DFW', 'DEN', 'LAX']
flights_df = flights_df[(flights_df['Origin'].isin(top_airports)) & (flights_df['Dest'].isin(top_airports))]

print(f"Loaded {len(flights_df)} flight records.")

print("Loading Weather Data...")
weather_file = "data/weather_2023_01.csv"
weather_df = pd.read_csv(weather_file)
# Rename columns
weather_df.rename(columns={'station': 'Airport', 'valid': 'DateTime', 'tmpf': 'Temp_F', 'sknt': 'Wind_Speed_kt', 'vsby': 'Visibility_mi', 'p01m': 'Precip_in'}, inplace=True)

# --- 2. Preprocess Data ---
# Flight Data
flights_df = flights_df[flights_df['Cancelled'] == 0] # Remove cancelled flights
flights_df.dropna(subset=['DepDelay'], inplace=True) # Remove missing target variable

# Create datetime for flights (Scheduled Departure Time)
def make_datetime(row):
    time_str = str(int(row['CRSDepTime'])).zfill(4)
    if time_str == '2400': time_str = '0000'
    try:
        return pd.to_datetime(row['FlightDate'] + ' ' + time_str[:2] + ':' + time_str[2:])
    except:
        return pd.NaT

flights_df['Scheduled_DateTime'] = flights_df.apply(make_datetime, axis=1)
flights_df.dropna(subset=['Scheduled_DateTime'], inplace=True)

# Proxy for ATC Congestion (Flights per hour at Origin)
flights_df['Hour'] = flights_df['Scheduled_DateTime'].dt.hour
flights_df['Date'] = flights_df['Scheduled_DateTime'].dt.date
congestion_df = flights_df.groupby(['Origin', 'Date', 'Hour']).size().reset_index(name='Origin_Traffic_Vol')
flights_df = flights_df.merge(congestion_df, on=['Origin', 'Date', 'Hour'], how='left')


# Weather Data
# Replace 'M' and 'T' with suitable values
weather_df.replace('M', np.nan, inplace=True)
weather_df.replace('T', 0.001, inplace=True) # Trace amount of rain
weather_df['DateTime'] = pd.to_datetime(weather_df['DateTime'])

# Convert to numeric
numeric_cols = ['Temp_F', 'Wind_Speed_kt', 'Visibility_mi', 'Precip_in']
for col in numeric_cols:
    weather_df[col] = pd.to_numeric(weather_df[col], errors='coerce')

# Interpolate missing weather values
weather_df = weather_df.sort_values(by=['Airport', 'DateTime'])
weather_df[numeric_cols] = weather_df.groupby('Airport')[numeric_cols].transform(lambda x: x.interpolate(method='linear').bfill().ffill())


# Merge Flight and Weather Data
# Round flight time to nearest hour to match with weather (assuming hourly or frequent weather reports)
flights_df['Weather_DateTime'] = flights_df['Scheduled_DateTime'].dt.round('h')
weather_df['Weather_DateTime'] = weather_df['DateTime'].dt.round('h')

# Take the mean weather per hour per airport to avoid duplicate weather rows
weather_hourly = weather_df.groupby(['Airport', 'Weather_DateTime'])[numeric_cols].mean().reset_index()

merged_df = flights_df.merge(weather_hourly, left_on=['Origin', 'Weather_DateTime'], right_on=['Airport', 'Weather_DateTime'], how='left')
merged_df.drop(columns=['Airport'], inplace=True) # drop redundant column

# Fill remaining NaNs in weather with median
for col in numeric_cols:
    merged_df[col] = merged_df[col].fillna(merged_df[col].median())

print(f"Final merged dataset has {len(merged_df)} rows.")

# Feature Engineering
merged_df['Target_Delay_Class'] = (merged_df['DepDelay'] > 15).astype(int) # 1 if delayed > 15 mins
merged_df['Month'] = merged_df['Scheduled_DateTime'].dt.month
merged_df['DayOfWeek'] = merged_df['Scheduled_DateTime'].dt.dayofweek

features = ['Reporting_Airline', 'Origin', 'Dest', 'Distance', 'Origin_Traffic_Vol', 'Month', 'DayOfWeek', 'Hour', 'Temp_F', 'Wind_Speed_kt', 'Visibility_mi', 'Precip_in']
target_reg = 'DepDelay'
target_cls = 'Target_Delay_Class'

df_modeling = merged_df[features + [target_reg, target_cls]].copy()

# Encode Categoricals
df_modeling = pd.get_dummies(df_modeling, columns=['Reporting_Airline', 'Origin', 'Dest'], drop_first=True)

# --- 3. Exploratory Data Analysis (EDA) ---
sns.set_theme(style="whitegrid")

# 1. Delay Distribution
plt.figure(figsize=(10, 5))
sns.histplot(merged_df[merged_df['DepDelay'] <= 120]['DepDelay'], bins=50, kde=True)
plt.title('Distribution of Departure Delays (<= 120 mins)')
plt.xlabel('Departure Delay (minutes)')
plt.ylabel('Frequency')
plt.savefig('delay_dist.png')
plt.show()

# 2. Weather vs Delay Relationships (Visibility)
plt.figure(figsize=(10, 5))
sns.boxplot(x=pd.qcut(merged_df['Visibility_mi'], q=4, duplicates='drop'), y='DepDelay', data=merged_df)
plt.title('Departure Delay vs Visibility (Quartiles)')
plt.ylim(-20, 100)
plt.xlabel('Visibility (miles)')
plt.ylabel('Departure Delay (minutes)')
plt.savefig('weather_delay_visibility.png')
plt.show()

# 3. Airport Congestion Patterns
plt.figure(figsize=(10, 5))
sns.scatterplot(x='Origin_Traffic_Vol', y='DepDelay', data=merged_df, alpha=0.3)
plt.title('Departure Delay vs Origin Traffic Volume (Hourly)')
plt.xlabel('Number of Flights at Origin (Hour)')
plt.ylabel('Departure Delay (minutes)')
plt.ylim(-20, 200)
plt.savefig('congestion_delay.png')
plt.show()

# 4. Correlation Heatmap
plt.figure(figsize=(12, 10))
corr = df_modeling.corr()
# Get top 15 correlated features with DepDelay
top_corr_features = corr['DepDelay'].abs().sort_values(ascending=False).head(15).index
sns.heatmap(df_modeling[top_corr_features].corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap (Top Features)')
plt.savefig('correlation_heatmap.png')
plt.show()

print("EDA Complete. Plots saved.")
''')

nb['cells'].append(preprocessing_eda_cell)

with open('Flight_Delay_Prediction.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Appended Preprocessing and EDA cells.")
