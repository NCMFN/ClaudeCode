import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import os
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier, plot_importance
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve, precision_recall_curve
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import GridSearchCV
import shap
import pickle

# Create directory for images if it doesn't exist
os.makedirs('SAF_Compatibility_Prediction/images', exist_ok=True)

# 1. Load Data
df = pd.read_csv('SAF_Compatibility_Prediction/saf_dataset.csv')
print("Dataset Loaded. Shape:", df.shape)

# --- ADDITION 1: Class Distribution Plot ---
plt.figure(figsize=(6, 4))
sns.countplot(data=df, x='Drop_in_Compatible', palette='viridis')
plt.title('Target Variable Distribution (Class Imbalance)')
plt.savefig('SAF_Compatibility_Prediction/images/class_distribution.png')
plt.close()

# 2. Exploratory Data Analysis (EDA)
plt.figure(figsize=(12, 10))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap of SAF Properties')
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/correlation_heatmap.png')
plt.close()

# --- ADDITION 2: Pairplot of top features ---
# Select top features based on domain knowledge for a cleaner pairplot
top_features = ['Kinematic_Viscosity_mms2', 'Aromatics_vol_percent', 'Density_kgm3', 'Drop_in_Compatible']
plt.figure(figsize=(10, 8))
sns.pairplot(df[top_features], hue='Drop_in_Compatible', palette='Set1', diag_kind='kde')
plt.savefig('SAF_Compatibility_Prediction/images/feature_pairplot.png')
plt.close()

# --- ADDITION 3-6: Boxplots for individual features against the target ---
features_to_plot = ['Kinematic_Viscosity_mms2', 'Aromatics_vol_percent', 'Flash_Point_C', 'Freezing_Point_C']
for feature in features_to_plot:
    plt.figure(figsize=(6, 4))
    sns.boxplot(x='Drop_in_Compatible', y=feature, data=df, palette='Set2')
    plt.title(f'Distribution of {feature} by Compatibility')
    plt.savefig(f'SAF_Compatibility_Prediction/images/boxplot_{feature}.png')
    plt.close()


# 3. Feature and Target Separation
X = df.drop('Drop_in_Compatible', axis=1)
y = df['Drop_in_Compatible'].astype(int)

# 4. Train-Test Split FIRST
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 5. Handle Missing Values (Fit ONLY on training data to prevent data leakage)
imputer = SimpleImputer(strategy='median')
X_train_imputed = pd.DataFrame(imputer.fit_transform(X_train), columns=X_train.columns)
X_test_imputed = pd.DataFrame(imputer.transform(X_test), columns=X_test.columns)

# 6. Apply SMOTE to handle class imbalance (on training data only)
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_imputed, y_train)

# 7. Preprocessing: Standardize features (Fit ONLY on training data)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test_imputed)

print("Preprocessing complete. Training set shape after SMOTE:", X_train_scaled.shape)


# --- Model Development and Evaluation ---
# Initialize models
models = {
    'Logistic Regression': LogisticRegression(random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
}

results = {}

# Train and evaluate traditional ML models
for name, model in models.items():
    model.fit(X_train_scaled, y_train_resampled)
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]

    results[name] = {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1-Score': f1_score(y_test, y_pred),
        'ROC-AUC': roc_auc_score(y_test, y_prob),
        'y_prob': y_prob, # Save for PR curve
        'model': model
    }

    # Plot Confusion Matrix
    plt.figure(figsize=(6, 4))
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues')
    plt.title(f'{name} Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'SAF_Compatibility_Prediction/images/{name.replace(" ", "_").lower()}_confusion_matrix.png')
    plt.close()

# Neural Network
nn_model = Sequential([
    Dense(32, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    Dropout(0.3),
    Dense(16, activation='relu'),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])

nn_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
nn_history = nn_model.fit(X_train_scaled, y_train_resampled, epochs=50, batch_size=32, validation_split=0.2, verbose=0)

y_pred_nn_prob = nn_model.predict(X_test_scaled).flatten()
y_pred_nn = (y_pred_nn_prob > 0.5).astype(int)

results['Neural Network'] = {
    'Accuracy': accuracy_score(y_test, y_pred_nn),
    'Precision': precision_score(y_test, y_pred_nn),
    'Recall': recall_score(y_test, y_pred_nn),
    'F1-Score': f1_score(y_test, y_pred_nn),
    'ROC-AUC': roc_auc_score(y_test, y_pred_nn_prob),
    'y_prob': y_pred_nn_prob,
    'model': nn_model
}

# Neural Network Confusion Matrix
plt.figure(figsize=(6, 4))
sns.heatmap(confusion_matrix(y_test, y_pred_nn), annot=True, fmt='d', cmap='Blues')
plt.title('Neural Network Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/neural_network_confusion_matrix.png')
plt.close()

# Print Results
print("\n--- Model Performance Comparison ---")
results_df = pd.DataFrame(results).T.drop(['model', 'y_prob'], axis=1)
print(results_df)

# Plot ROC Curves
plt.figure(figsize=(10, 8))
for name in results.keys():
    fpr, tpr, _ = roc_curve(y_test, results[name]['y_prob'])
    plt.plot(fpr, tpr, label=f'{name} (AUC = {results[name]["ROC-AUC"]:.3f})')

plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves')
plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/roc_curves.png')
plt.close()

# --- ADDITION 7: Precision-Recall Curves ---
plt.figure(figsize=(10, 8))
for name in results.keys():
    precision, recall, _ = precision_recall_curve(y_test, results[name]['y_prob'])
    plt.plot(recall, precision, label=f'{name}')

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curves')
plt.legend(loc='lower left')
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/precision_recall_curves.png')
plt.close()


# --- Model Interpretation and Tuning ---

print("\n--- Hyperparameter Tuning (XGBoost) ---")
# Limit parameter space to keep training fast for this demonstration
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1]
}

xgb = XGBClassifier(eval_metric='logloss', random_state=42)
grid_search = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=3, scoring='f1', n_jobs=-1)
grid_search.fit(X_train_scaled, y_train_resampled)

best_xgb = grid_search.best_estimator_
print(f"Best parameters: {grid_search.best_params_}")

y_pred_best = best_xgb.predict(X_test_scaled)
print("Tuned XGBoost F1-Score:", f1_score(y_test, y_pred_best))
print("Tuned XGBoost Accuracy:", accuracy_score(y_test, y_pred_best))

# --- ADDITION 8: XGBoost Built-in Feature Importance Bar Plot ---
plt.figure(figsize=(10, 6))
# Get feature names back from standard scaler
best_xgb.get_booster().feature_names = list(X.columns)
plot_importance(best_xgb, max_num_features=10, importance_type='weight', title='XGBoost Feature Importance (Weight)')
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/xgboost_feature_importance.png')
plt.close()


# SHAP Feature Importance
print("\n--- SHAP Feature Importance ---")
# SHAP on the scaled test set
explainer = shap.TreeExplainer(best_xgb)
shap_values = explainer.shap_values(X_test_scaled)

plt.figure(figsize=(10, 8))
shap.summary_plot(shap_values, X_test_scaled, feature_names=X.columns, show=False)
plt.tight_layout()
plt.savefig('SAF_Compatibility_Prediction/images/shap_summary.png')
plt.close()


# Save the Best Model and Scaler
print("\n--- Saving Model and Scaler ---")
with open('SAF_Compatibility_Prediction/best_saf_model.pkl', 'wb') as f:
    pickle.dump(best_xgb, f)

with open('SAF_Compatibility_Prediction/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

with open('SAF_Compatibility_Prediction/imputer.pkl', 'wb') as f:
    pickle.dump(imputer, f)
print("Model, Scaler, and Imputer saved successfully.")

# Prediction API Function
def predict_saf_compatibility(features_dict):
    """
    Predicts if a SAF blend is drop-in compatible.
    features_dict: dict containing the 9 feature values
    """
    df_input = pd.DataFrame([features_dict])
    # Ensure correct column order
    df_input = df_input[X.columns]

    # Impute missing and scale
    imputed_input = pd.DataFrame(imputer.transform(df_input), columns=df_input.columns)
    scaled_input = scaler.transform(imputed_input)

    # Predict
    prediction = best_xgb.predict(scaled_input)[0]
    probability = best_xgb.predict_proba(scaled_input)[0][1]

    return {
        "Drop_in_Compatible": int(prediction),
        "Probability": float(probability)
    }
