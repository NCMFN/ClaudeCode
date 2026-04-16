import nbformat as nbf

with open('Flight_Delay_Prediction.ipynb', 'r') as f:
    nb = nbf.read(f, as_version=4)

modeling_cell = nbf.v4.new_code_cell('''from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, Input
import time

# --- 4. Model Development & Training ---

# Prepare Data Splits
X = df_modeling.drop(columns=['DepDelay', 'Target_Delay_Class'])
y_reg = df_modeling['DepDelay']
y_cls = df_modeling['Target_Delay_Class']

X_train, X_test, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)
_, _, y_train_cls, y_test_cls = train_test_split(X, y_cls, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

results = {}

# 1. Classical ML: Linear Regression
print("Training Linear Regression...")
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train_reg)
lr_preds = lr_model.predict(X_test_scaled)
results['Linear Regression'] = {
    'MAE': mean_absolute_error(y_test_reg, lr_preds),
    'RMSE': np.sqrt(mean_squared_error(y_test_reg, lr_preds)),
    'R2': r2_score(y_test_reg, lr_preds)
}

# 2. Classical ML: Random Forest (Subset for speed)
print("Training Random Forest...")
rf_model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train_scaled[:10000], y_train_reg[:10000]) # Subsample for training time
rf_preds = rf_model.predict(X_test_scaled)
results['Random Forest'] = {
    'MAE': mean_absolute_error(y_test_reg, rf_preds),
    'RMSE': np.sqrt(mean_squared_error(y_test_reg, rf_preds)),
    'R2': r2_score(y_test_reg, rf_preds)
}

# 3. Classical ML: XGBoost
print("Training XGBoost...")
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1)
xgb_model.fit(X_train_scaled, y_train_reg)
xgb_preds = xgb_model.predict(X_test_scaled)
results['XGBoost'] = {
    'MAE': mean_absolute_error(y_test_reg, xgb_preds),
    'RMSE': np.sqrt(mean_squared_error(y_test_reg, xgb_preds)),
    'R2': r2_score(y_test_reg, xgb_preds)
}

# 4. Deep Learning: Feedforward Neural Network
print("Training Feedforward Neural Network...")
nn_model = Sequential([
    Input(shape=(X_train_scaled.shape[1],)),
    Dense(64, activation='relu'),
    Dropout(0.2),
    Dense(32, activation='relu'),
    Dense(1) # Regression output
])
nn_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
# Train on a subset or full data, epochs kept low for demonstration
nn_history = nn_model.fit(X_train_scaled, y_train_reg, validation_split=0.2, epochs=10, batch_size=256, verbose=0)
nn_preds = nn_model.predict(X_test_scaled).flatten()
results['Feedforward NN'] = {
    'MAE': mean_absolute_error(y_test_reg, nn_preds),
    'RMSE': np.sqrt(mean_squared_error(y_test_reg, nn_preds)),
    'R2': r2_score(y_test_reg, nn_preds)
}
nn_model.save('ffnn_model.h5')

# 5. Deep Learning: LSTM (Treating features as a sequence of 1 timestep for demonstration)
print("Training LSTM...")
X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))

lstm_model = Sequential([
    Input(shape=(X_train_lstm.shape[1], X_train_lstm.shape[2])),
    LSTM(32, activation='relu'),
    Dense(1)
])
lstm_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
lstm_model.fit(X_train_lstm, y_train_reg, validation_split=0.2, epochs=5, batch_size=256, verbose=0)
lstm_preds = lstm_model.predict(X_test_lstm).flatten()
results['LSTM'] = {
    'MAE': mean_absolute_error(y_test_reg, lstm_preds),
    'RMSE': np.sqrt(mean_squared_error(y_test_reg, lstm_preds)),
    'R2': r2_score(y_test_reg, lstm_preds)
}
lstm_model.save('lstm_model.h5')


# --- 5. Model Evaluation & Visualization ---
print("\\nModel Evaluation Results:")
results_df = pd.DataFrame(results).T
print(results_df)

# Plot Model Performance
results_df[['MAE', 'RMSE']].plot(kind='bar', figsize=(10, 6))
plt.title('Model Performance Comparison (MAE & RMSE)')
plt.ylabel('Error (minutes)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('model_comparison.png')
plt.show()

# Feature Importance (XGBoost)
plt.figure(figsize=(10, 6))
feat_importances = pd.Series(xgb_model.feature_importances_, index=X.columns)
feat_importances.nlargest(10).plot(kind='barh')
plt.title('Top 10 Feature Importances (XGBoost)')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.show()

# Prediction vs Actual (XGBoost)
plt.figure(figsize=(8, 8))
plt.scatter(y_test_reg[:1000], xgb_preds[:1000], alpha=0.3)
plt.plot([y_test_reg.min(), 200], [y_test_reg.min(), 200], 'r--')
plt.xlabel('Actual Delay (mins)')
plt.ylabel('Predicted Delay (mins)')
plt.title('XGBoost: Predicted vs Actual Delay (Sample)')
plt.xlim(-50, 200)
plt.ylim(-50, 200)
plt.savefig('pred_vs_actual.png')
plt.show()
''')

nb['cells'].append(modeling_cell)

with open('Flight_Delay_Prediction.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Appended Modeling cells.")
