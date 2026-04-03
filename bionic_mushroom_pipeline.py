import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings

from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

warnings.filterwarnings('ignore')

# ---------------------------------------------------------
# 1. Data Preparation (Simulation)
# ---------------------------------------------------------
def simulate_data(n_samples=1000):
    np.random.seed(42)

    # Features
    # Light intensity (lux)
    light = np.random.uniform(100, 10000, n_samples)
    # Humidity (%)
    humidity = np.random.uniform(30, 95, n_samples)
    # Bacterial colony density (OD600 or cells/mL)
    bacterial_density = np.random.uniform(0.1, 2.5, n_samples)

    # Introduce some missing values randomly
    light[np.random.choice(n_samples, 20, replace=False)] = np.nan
    humidity[np.random.choice(n_samples, 20, replace=False)] = np.nan
    bacterial_density[np.random.choice(n_samples, 20, replace=False)] = np.nan

    # Target (Current Density: mA/m2)
    # Underlying relationship (non-linear with interactions)
    base_current = 10.0
    current_density = (
        base_current
        + 0.05 * light
        + 0.2 * humidity
        + 15.0 * bacterial_density
        + 0.001 * (light * humidity)  # Interaction
        - 0.5 * (bacterial_density ** 2)
        + np.random.normal(0, 5.0, n_samples) # Noise
    )

    df = pd.DataFrame({
        'Light_Intensity': light,
        'Humidity': humidity,
        'Bacterial_Density': bacterial_density,
        'Current_Density': current_density
    })

    return df

df = simulate_data()
print("Original Dataset Shape:", df.shape)

# Handling Missing Values (Imputation with median)
print("Missing values before handling:\n", df.isnull().sum())
df.fillna(df.median(), inplace=True)
print("Missing values after handling:\n", df.isnull().sum())

# ---------------------------------------------------------
# 2. Exploratory Data Analysis & Feature Engineering
# ---------------------------------------------------------
# Feature Engineering: Interaction Features
df['Light_x_Humidity'] = df['Light_Intensity'] * df['Humidity']

# EDA: Feature vs Target Plots
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
sns.scatterplot(data=df, x='Light_Intensity', y='Current_Density', ax=axes[0], alpha=0.6)
axes[0].set_title('Light Intensity vs Current Density')
sns.scatterplot(data=df, x='Humidity', y='Current_Density', ax=axes[1], alpha=0.6)
axes[1].set_title('Humidity vs Current Density')
sns.scatterplot(data=df, x='Bacterial_Density', y='Current_Density', ax=axes[2], alpha=0.6)
axes[2].set_title('Bacterial Density vs Current Density')
plt.tight_layout()
plt.savefig('eda_scatter_plots.png')
plt.close()

# EDA: Correlation Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.savefig('correlation_heatmap.png')
plt.close()

# Split Features and Target
X = df.drop('Current_Density', axis=1)
y = df['Current_Density']

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Convert back to DataFrame for easier handling
X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)

# ---------------------------------------------------------
# 3 & 4. Model Development & Evaluation
# ---------------------------------------------------------
def evaluate_model(y_true, y_pred, model_name):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    print(f"--- {model_name} ---")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE:  {mae:.4f}")
    print(f"R2:   {r2:.4f}\n")
    return {'RMSE': rmse, 'MAE': mae, 'R2': r2}

results = {}

# A. Linear Regression
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)
y_pred_lr = lr_model.predict(X_test_scaled)
results['Linear Regression'] = evaluate_model(y_test, y_pred_lr, "Linear Regression")

# Cross-Validation for Linear Regression
cv_scores_lr = cross_val_score(lr_model, X_train_scaled, y_train, cv=5, scoring='r2')
print(f"Linear Regression CV R2: {cv_scores_lr.mean():.4f} (+/- {cv_scores_lr.std() * 2:.4f})\n")


# B. Random Forest Regressor (with Hyperparameter Tuning)
rf_base = RandomForestRegressor(random_state=42)

# ---------------------------------------------------------
# 5. Optimization (Hyperparameter Tuning for RF)
# ---------------------------------------------------------
param_dist = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_random = RandomizedSearchCV(
    estimator=rf_base,
    param_distributions=param_dist,
    n_iter=10,
    cv=3,
    verbose=0,
    random_state=42,
    n_jobs=-1,
    scoring='neg_mean_squared_error'
)
rf_random.fit(X_train_scaled, y_train)

best_rf = rf_random.best_estimator_
y_pred_rf = best_rf.predict(X_test_scaled)
results['Random Forest'] = evaluate_model(y_test, y_pred_rf, "Random Forest (Tuned)")

# Feature Importance Analysis
feature_importances = pd.Series(best_rf.feature_importances_, index=X.columns)
feature_importances.sort_values(ascending=True).plot(kind='barh', color='skyblue')
plt.title('Feature Importances (Random Forest)')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.close()

# ---------------------------------------------------------
# 6. Deep Learning Model (Keras/TensorFlow)
# ---------------------------------------------------------
nn_model = Sequential([
    Input(shape=(X_train_scaled.shape[1],)),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(1, activation='linear')
])

nn_model.compile(optimizer=Adam(learning_rate=0.01), loss='mse', metrics=['mae'])

# Train the model
history = nn_model.fit(
    X_train_scaled, y_train,
    validation_split=0.2,
    epochs=100,
    batch_size=32,
    verbose=0
)

y_pred_nn = nn_model.predict(X_test_scaled).flatten()
results['Neural Network'] = evaluate_model(y_test, y_pred_nn, "Neural Network")

# Plot Training History
plt.figure(figsize=(8, 5))
plt.plot(history.history['loss'], label='Train Loss (MSE)')
plt.plot(history.history['val_loss'], label='Validation Loss (MSE)')
plt.title('Neural Network Training History')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.tight_layout()
plt.savefig('nn_training_history.png')
plt.close()

# ---------------------------------------------------------
# 7. Visualization: Predictions vs Actual & Residuals
# ---------------------------------------------------------
# Determine best model based on R2 on test set
best_model_name = max(results, key=lambda k: results[k]['R2'])
print(f"*** Best Model Identified: {best_model_name} ***\n")

if best_model_name == 'Linear Regression':
    best_preds = y_pred_lr
elif best_model_name == 'Random Forest':
    best_preds = y_pred_rf
else:
    best_preds = y_pred_nn

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Prediction vs Actual
axes[0].scatter(y_test, best_preds, alpha=0.6, color='blue')
axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
axes[0].set_title(f'Actual vs Predicted ({best_model_name})')
axes[0].set_xlabel('Actual Current Density')
axes[0].set_ylabel('Predicted Current Density')

# Residuals
residuals = y_test - best_preds
axes[1].scatter(best_preds, residuals, alpha=0.6, color='purple')
axes[1].axhline(y=0, color='r', linestyle='--')
axes[1].set_title(f'Residual Plot ({best_model_name})')
axes[1].set_xlabel('Predicted Current Density')
axes[1].set_ylabel('Residuals')

plt.tight_layout()
plt.savefig('predictions_residuals.png')
plt.close()

# ---------------------------------------------------------
# 8. Output & Bonus (Prediction Function & Model Saving)
# ---------------------------------------------------------
# Save Models
joblib.dump(best_rf, 'random_forest_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
nn_model.save('neural_network_model.h5')  # Recommended to use .keras but prompt asked for .h5
print("Models saved successfully.\n")

def predict_current_density(light, humidity, bacterial_density):
    """
    Predict Current Density for new inputs using the best model.
    """
    # Create DataFrame for the new input
    input_data = pd.DataFrame({
        'Light_Intensity': [light],
        'Humidity': [humidity],
        'Bacterial_Density': [bacterial_density]
    })

    # Add interaction feature
    input_data['Light_x_Humidity'] = input_data['Light_Intensity'] * input_data['Humidity']

    # Scale features
    input_scaled = scaler.transform(input_data)

    # Predict using Random Forest (assuming it's a top performer, or dynamically use the best)
    # Using the best_rf here as an example since we have the object available
    prediction_rf = best_rf.predict(input_scaled)[0]
    prediction_nn = nn_model.predict(input_scaled, verbose=0)[0][0]

    print(f"Prediction for Inputs (Light: {light}, Humidity: {humidity}, Bact. Density: {bacterial_density}):")
    print(f"  Random Forest Estimate: {prediction_rf:.2f} mA/m2")
    print(f"  Neural Network Estimate: {prediction_nn:.2f} mA/m2")

    return prediction_rf, prediction_nn

# Example usage of the prediction function
print("Testing Prediction Function:")
predict_current_density(light=5000, humidity=65, bacterial_density=1.2)

print("\nPipeline execution complete!")
