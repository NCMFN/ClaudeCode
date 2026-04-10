import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score, roc_auc_score, confusion_matrix
import os
from sklearn.impute import SimpleImputer

os.makedirs('outputs', exist_ok=True)

print("1. Data Integration & Preprocessing")
amphibio = pd.read_csv('data/AmphiBIO_v1.csv', encoding='latin1')
iucn = pd.read_csv('data/iucn_status_final.csv').dropna(subset=['IUCN_Status'])
climate = pd.read_csv('data/species_climate.csv')

df = amphibio.merge(iucn, on='Species', how='inner')
df = df.merge(climate, on='Species', how='inner')

df = df[df['IUCN_Status'].isin(['LEAST_CONCERN', 'NEAR_THREATENED', 'VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED'])]
df['Threatened'] = df['IUCN_Status'].apply(lambda x: 1 if x in ['VULNERABLE', 'ENDANGERED', 'CRITICALLY_ENDANGERED'] else 0)

features_to_use = [
    'Fos', 'Ter', 'Aqu', 'Arb', 'Leaves', 'Flowers', 'Seeds', 'Fruits', 'Arthro', 'Vert', 'Diu', 'Noc', 'Crepu',
    'Wet_warm', 'Wet_cold', 'Dry_warm', 'Dry_cold', 'Body_mass_g', 'Age_at_maturity_min_y', 'Body_size_mm',
    'Longevity_max_y', 'Litter_size_max_n', 'Reproductive_output_y', 'Dir', 'Lar', 'Viv',
    'range_size_deg2'
] + [f'bio_{i}_mean' for i in range(1, 20)]

for col in features_to_use:
    df[col] = pd.to_numeric(df[col], errors='coerce')

X = df[features_to_use].copy()
y = df['Threatened'].values

imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_imputed, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)

print("\n2. Model Training - Random Forest")
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train_res, y_train_res)
y_pred_rf = rf.predict(X_test_scaled)
y_prob_rf = rf.predict_proba(X_test_scaled)[:, 1]

print("Random Forest Accuracy:", accuracy_score(y_test, y_pred_rf))
print("Random Forest ROC-AUC:", roc_auc_score(y_test, y_prob_rf))

print("\n3. Model Training - XGBoost")
xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
xgb.fit(X_train_res, y_train_res)
y_pred_xgb = xgb.predict(X_test_scaled)
y_prob_xgb = xgb.predict_proba(X_test_scaled)[:, 1]

print("XGBoost Accuracy:", accuracy_score(y_test, y_pred_xgb))
print("XGBoost ROC-AUC:", roc_auc_score(y_test, y_prob_xgb))
print(classification_report(y_test, y_pred_xgb))

# Feature Importance
importances = xgb.feature_importances_
indices = np.argsort(importances)[::-1]
top_n = 15

plt.figure(figsize=(10, 6))
plt.title('Top 15 Feature Importances (XGBoost)')
plt.bar(range(top_n), importances[indices][:top_n], align="center")
plt.xticks(range(top_n), [features_to_use[i] for i in indices][:top_n], rotation=45, ha='right')
plt.tight_layout()
plt.savefig('outputs/feature_importance.png')
plt.close()

top_features = [features_to_use[i] for i in indices][:10]
plt.figure(figsize=(10, 8))
sns.heatmap(df[top_features + ['Threatened']].corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig('outputs/correlation_heatmap.png')
plt.close()

from sklearn.metrics import roc_curve
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_prob_rf)
fpr_xgb, tpr_xgb, _ = roc_curve(y_test, y_prob_xgb)

plt.figure(figsize=(8,6))
plt.plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC = {roc_auc_score(y_test, y_prob_rf):.2f})')
plt.plot(fpr_xgb, tpr_xgb, label=f'XGBoost (AUC = {roc_auc_score(y_test, y_prob_xgb):.2f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves')
plt.legend()
plt.tight_layout()
plt.savefig('outputs/roc_curves.png')
plt.close()

cm = confusion_matrix(y_test, y_pred_xgb)
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Non-Threatened', 'Threatened'], yticklabels=['Non-Threatened', 'Threatened'])
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix - XGBoost')
plt.tight_layout()
plt.savefig('outputs/confusion_matrix.png')
plt.close()

# Neural Network Model (TensorFlow/Keras)
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping

    print("\n4. Model Training - Neural Network")
    nn = Sequential([
        Dense(64, activation='relu', input_shape=(X_train_res.shape[1],)),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')
    ])

    nn.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    nn.fit(X_train_res, y_train_res, epochs=100, batch_size=32, validation_data=(X_test_scaled, y_test), callbacks=[early_stop], verbose=0)

    y_prob_nn = nn.predict(X_test_scaled).flatten()
    y_pred_nn = (y_prob_nn > 0.5).astype(int)

    print("Neural Network Accuracy:", accuracy_score(y_test, y_pred_nn))
    print("Neural Network ROC-AUC:", roc_auc_score(y_test, y_prob_nn))

    nn.save('outputs/amphibian_nn_model.h5')
except Exception as e:
    print("Failed to train Neural Network:", e)

import joblib
joblib.dump(xgb, 'outputs/xgboost_model.pkl')
joblib.dump(scaler, 'outputs/scaler.pkl')

print("Pipeline completed successfully. Artifacts saved in 'outputs/'.")
