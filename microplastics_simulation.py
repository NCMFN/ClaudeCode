import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os

# Set a random seed for reproducibility
np.random.seed(42)

# Number of samples based on the study (229 blood, 227 fecal - we'll simulate 229 participants)
num_samples = 229

# --- 1. Simulate Demographics, Socioeconomic, and Lifestyle Data ---
# Age: normal distribution around 40, clipped between 18 and 80
age = np.clip(np.random.normal(40, 15, num_samples), 18, 80).astype(int)

# Sex: binary, roughly equal distribution
sex = np.random.choice(['Male', 'Female'], num_samples)

# BMI: normal distribution around 25
bmi = np.random.normal(25, 4, num_samples).round(1)

# Geographic Region: categorical
regions = ['Urban', 'Suburban', 'Rural']
region = np.random.choice(regions, num_samples, p=[0.5, 0.3, 0.2])

# Socioeconomic Indicators (Income Level): 1 = Low, 2 = Medium, 3 = High
income_level = np.random.choice(['Low', 'Medium', 'High'], num_samples, p=[0.3, 0.5, 0.2])

# --- 2. Simulate Dietary and Exposure Data ---
# Food category intake (g/day):
seafood_intake = np.random.gamma(shape=2, scale=20, size=num_samples).round(1)
meat_intake = np.random.normal(150, 50, num_samples).clip(0).round(1)
veg_intake = np.random.normal(250, 80, num_samples).clip(0).round(1)

# Water source type
water_sources = ['Tap Water', 'Bottled Water', 'Filtered Water', 'Well Water']
water_source = np.random.choice(water_sources, num_samples, p=[0.4, 0.3, 0.2, 0.1])

# Packaging exposure score (arbitrary scale 1-100)
packaging_score = np.random.normal(50, 15, num_samples).clip(1, 100).round(1)

# Processing level of diet (Scale 1-10, 10 = highly processed)
processing_level = np.random.normal(6, 2, num_samples).clip(1, 10).round(1)

# --- 3. Simulate Output (Target) Data ---
# Polymer types explicitly listed (7 types)
polymers = ['PE', 'PVC', 'PS', 'PET', 'PP', 'PA', 'PC']

# Create dictionaries to store blood and fecal concentrations (µg/mL or MPs/mL)
blood_mps = {}
fecal_mps = {}

# We simulate some correlation between inputs and outputs (valid approach in exposure science)
for poly in polymers:
    # Base baseline
    blood_base = np.random.exponential(scale=2.0, size=num_samples)
    fecal_base = np.random.exponential(scale=5.0, size=num_samples)

    # Add correlated variance
    if poly == 'PET':
        # PET highly associated with bottled water and packaging
        bottled_effect = (water_source == 'Bottled Water').astype(float) * np.random.normal(3.0, 1.0, num_samples)
        pack_effect = (packaging_score / 100) * np.random.normal(2.0, 0.5, num_samples)
        blood_mps[poly] = (blood_base + bottled_effect + pack_effect).clip(0).round(3)
    elif poly == 'PE':
        # PE associated with packaging and processing level
        pack_effect = (packaging_score / 100) * np.random.normal(1.5, 0.5, num_samples)
        proc_effect = (processing_level / 10) * np.random.normal(1.0, 0.5, num_samples)
        blood_mps[poly] = (blood_base + pack_effect + proc_effect).clip(0).round(3)
    elif poly == 'PS':
        # PS associated with seafood and processing
        sea_effect = (seafood_intake / 100) * np.random.normal(1.0, 0.3, num_samples)
        blood_mps[poly] = (blood_base + sea_effect).clip(0).round(3)
    elif poly == 'PVC':
        # PVC associated with tap water (pipe infrastructure)
        tap_effect = (water_source == 'Tap Water').astype(float) * np.random.normal(2.0, 0.8, num_samples)
        blood_mps[poly] = (blood_base + tap_effect).clip(0).round(3)
    elif poly == 'PP':
        # PP associated with packaging
        pack_effect = (packaging_score / 100) * np.random.normal(1.8, 0.6, num_samples)
        blood_mps[poly] = (blood_base + pack_effect).clip(0).round(3)
    elif poly == 'PA':
        # PA general baseline
        blood_mps[poly] = blood_base.clip(0).round(3)
    elif poly == 'PC':
        # PC associated with packaging
        pack_effect = (packaging_score / 100) * np.random.normal(1.2, 0.4, num_samples)
        blood_mps[poly] = (blood_base + pack_effect).clip(0).round(3)

    # Fecal concentrations are generally higher but correlated with blood
    fecal_mps[poly] = (blood_mps[poly] * np.random.normal(3.0, 1.0, num_samples) + fecal_base).clip(0).round(3)

# Introduce a few missing values in Fecal samples (since study had 229 blood, 227 fecal)
missing_indices = np.random.choice(num_samples, 2, replace=False)
for poly in polymers:
    fecal_mps[poly][missing_indices] = np.nan

# --- 4. Assemble the DataFrame ---
data = {
    'Participant_ID': [f'P{str(i).zfill(3)}' for i in range(1, num_samples + 1)],
    'Age': age,
    'Sex': sex,
    'BMI': bmi,
    'Region': region,
    'Income_Level': income_level,
    'Seafood_Intake_g_day': seafood_intake,
    'Meat_Intake_g_day': meat_intake,
    'Veg_Intake_g_day': veg_intake,
    'Water_Source': water_source,
    'Packaging_Exposure_Score': packaging_score,
    'Processing_Level_of_Diet': processing_level,
}

# Add blood targets
for poly in polymers:
    data[f'Blood_{poly}_ug_mL'] = blood_mps[poly]

# Add fecal targets
for poly in polymers:
    data[f'Fecal_{poly}_ug_mL'] = fecal_mps[poly]

df = pd.DataFrame(data)

# Calculate total blood MP concentration
df['Total_Blood_MP_ug_mL'] = df[[f'Blood_{poly}_ug_mL' for poly in polymers]].sum(axis=1)

# Save the dataset
df.to_csv('synthetic_microplastics_data.csv', index=False)
print(f"Dataset successfully synthesized and saved as 'synthetic_microplastics_data.csv' with shape: {df.shape}")

# --- 5. Machine Learning Analysis (Identifying Key Predictors) ---
print("\n--- Machine Learning Analysis ---")
print("Training a Random Forest model to predict 'Total_Blood_MP_ug_mL' based on features...\n")

# Prepare features (X) and target (y)
features = ['Age', 'Sex', 'BMI', 'Region', 'Income_Level', 'Seafood_Intake_g_day',
            'Meat_Intake_g_day', 'Veg_Intake_g_day', 'Water_Source',
            'Packaging_Exposure_Score', 'Processing_Level_of_Diet']

X = df[features].copy()
y = df['Total_Blood_MP_ug_mL']

# Encode categorical variables
le = LabelEncoder()
X['Sex'] = le.fit_transform(X['Sex'])
X['Region'] = le.fit_transform(X['Region'])
X['Income_Level'] = le.fit_transform(X['Income_Level'])

# For Water_Source, we can use one-hot encoding or label encoding. We'll use label encoding here for tree-based models.
X['Water_Source'] = le.fit_transform(X['Water_Source'])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Calculate R^2 score
score = rf_model.score(X_test, y_test)
print(f"Model Test R^2 Score: {score:.4f}")

# Extract and display feature importances
importances = rf_model.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print("\nKey Exposure Predictors (Feature Importances):")
print(feature_importance_df.to_string(index=False))

# Optional limitation statement as per user memory (avoid assuming causality)
print("\nNote: This analysis uses a simulated dataset mimicking the study distributions.")
print("The machine learning feature importances represent correlations and predictive power, not necessarily causality.")
print("Uncertainties such as measurement variability or self-reported dietary inconsistencies should be considered.")
