import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Create outputs directory
os.makedirs("outputs", exist_ok=True)

print("Loading dataset...")
try:
    df = pd.read_csv("microplastics_dataset.csv")
    print(f"Dataset loaded successfully with shape: {df.shape}")
except FileNotFoundError:
    print("Error: Dataset not found. Please ensure 'microplastics_dataset.csv' is in the current directory.")
    exit(1)

# Display dataset info
print(df.info())
print(df.describe())

# ==========================================
# 2. Exploratory Data Analysis (EDA)
# ==========================================
print("Generating EDA plots...")

# Set style for publication-quality plots
sns.set_theme(style="whitegrid")

# 1. Distribution of Target Variable
plt.figure(figsize=(8, 5))
ax = sns.countplot(data=df, x='Exposure_Risk', order=['Negligible', 'Low', 'High'], palette='viridis')
plt.title('Distribution of Exposure Risk Levels', fontsize=14)
plt.ylabel('Count')
plt.xlabel('Exposure Risk')
# Add counts on top of bars
for p in ax.patches:
    ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='baseline', fontsize=11, color='black', xytext=(0, 5),
                textcoords='offset points')
plt.tight_layout()
plt.savefig("outputs/1_exposure_risk_distribution.png", dpi=300)
plt.close()

# 2. Correlation Heatmap (Numerical features)
numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
plt.figure(figsize=(10, 8))
corr = df[numerical_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', square=True, linewidths=.5)
plt.title('Correlation Heatmap of Dietary & Demographic Features', fontsize=14)
plt.tight_layout()
plt.savefig("outputs/2_correlation_heatmap.png", dpi=300)
plt.close()

# 3. Scatter Plot: Bottled Water vs Risk
# Map categorical target to numerical for plotting trend
risk_mapping = {'Negligible': 0, 'Low': 1, 'High': 2}
df['Risk_Numeric'] = df['Exposure_Risk'].map(risk_mapping)

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='Exposure_Risk', y='Bottled_Water_Freq_week', hue='Setting',
            order=['Negligible', 'Low', 'High'], palette='Set2')
plt.title('Bottled Water Consumption vs Exposure Risk by Setting', fontsize=14)
plt.ylabel('Bottled Water Freq (times/week)')
plt.xlabel('Exposure Risk')
plt.tight_layout()
plt.savefig("outputs/3_bottled_water_vs_risk.png", dpi=300)
plt.close()

# 4. Packaging Type Distribution
plt.figure(figsize=(8, 5))
sns.countplot(data=df, x='Primary_Packaging', hue='Exposure_Risk', palette='viridis')
plt.title('Exposure Risk by Primary Packaging Type', fontsize=14)
plt.ylabel('Count')
plt.xlabel('Packaging Type')
plt.legend(title='Exposure Risk')
plt.tight_layout()
plt.savefig("outputs/4_packaging_vs_risk.png", dpi=300)
plt.close()

print("EDA plots generated and saved to outputs/ directory.")

# ==========================================
# 3. Core Analysis & Modeling (XGBoost)
# ==========================================
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
import xgboost as xgb

print("Starting Core Analysis Pipeline...")

# Preprocessing
X = df.drop(columns=['Exposure_Risk', 'Risk_Numeric'], errors='ignore')
y = df['Exposure_Risk']

# Encode Categorical Features
# Ordinal encoding for Packaging as per reference (Non-Plastic < HDPE < LDPE < PET based on assumed risk)
pkg_categories = [['Non-Plastic', 'HDPE', 'LDPE', 'PET']]
ordinal_enc = OrdinalEncoder(categories=pkg_categories)
X['Primary_Packaging'] = ordinal_enc.fit_transform(X[['Primary_Packaging']])

# One-hot encoding for Setting and Water_Source
X = pd.get_dummies(X, columns=['Setting', 'Water_Source'], drop_first=True)

# Encode Target Variable
label_enc = LabelEncoder()
# Let's ensure the classes are ordered Negligible:0, Low:1, High:2
label_enc.fit(['Negligible', 'Low', 'High'])
y_encoded = label_enc.transform(y)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)

# Handle Class Imbalance using SMOTE
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train_scaled, y_train)
print(f"Original training shape: {X_train.shape}, SMOTE training shape: {X_train_smote.shape}")

# Model Training: XGBoost Classifier
# Using a base model structure suitable for the proposed task
xgb_model = xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=3,
    eval_metric='mlogloss',
    use_label_encoder=False,
    random_state=42,
    learning_rate=0.05,
    max_depth=5,
    n_estimators=100
)

# K-Fold Cross Validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(xgb_model, X_train_smote, y_train_smote, cv=cv, scoring='accuracy')
print(f"5-Fold CV Accuracy (SMOTE): {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

# Final Training and Evaluation
xgb_model.fit(X_train_smote, y_train_smote)
y_pred = xgb_model.predict(X_test_scaled)

print("\nClassification Report:")
class_names = label_enc.inverse_transform([0, 1, 2])
print(classification_report(y_test, y_pred, target_names=class_names))

# ==========================================
# 4. Results Visualization
# ==========================================

# Feature Importance Plot
plt.figure(figsize=(10, 6))
feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': xgb_model.feature_importances_
}).sort_values(by='Importance', ascending=False)

sns.barplot(data=feature_importance, x='Importance', y='Feature', palette='viridis')
plt.title('XGBoost Feature Importance for MP Risk Prediction', fontsize=14)
plt.tight_layout()
plt.savefig("outputs/5_feature_importance.png", dpi=300)
plt.close()

# Confusion Matrix
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.title('Confusion Matrix: Microplastic Load Risk', fontsize=14)
plt.ylabel('True Class')
plt.xlabel('Predicted Class')
plt.tight_layout()
plt.savefig("outputs/6_confusion_matrix.png", dpi=300)
plt.close()

print("Analysis complete. Model metrics and evaluation plots saved to outputs/ directory.")
