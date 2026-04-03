import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import joblib
import shap
import warnings
warnings.filterwarnings('ignore')

def generate_synthetic_data(n_samples=1000):
    """
    Simulates a dataset based on Microbial Fuel Cell (MFC) performance variables.
    Features: Light intensity, Humidity, Bacterial colony density.
    Target: Current Density (mA/m^2).
    """
    np.random.seed(42)

    # 1. Light intensity (Lux) - e.g., 1000 to 10000
    light_intensity = np.random.uniform(1000, 10000, n_samples)

    # 2. Humidity (%) - e.g., 40 to 90
    humidity = np.random.uniform(40, 90, n_samples)

    # 3. Bacterial colony density (OD600 or CFU/mL) - e.g., 0.1 to 2.0
    bacterial_density = np.random.uniform(0.1, 2.0, n_samples)

    # Generate Target: Current Density with some non-linear relationships and interactions
    # Formula: base + a*light + b*humidity + c*bacterial_density + d*(light*humidity) + noise
    current_density = (
        10.0 +
        0.005 * light_intensity +
        0.2 * humidity +
        15.0 * bacterial_density +
        0.0001 * (light_intensity * humidity) + # interaction
        np.random.normal(0, 5, n_samples) # noise
    )

    df = pd.DataFrame({
        'Light_Intensity': light_intensity,
        'Humidity': humidity,
        'Bacterial_Density': bacterial_density,
        'Current_Density': current_density
    })

    # Introduce some missing values to demonstrate handling
    missing_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
    df.loc[missing_indices, 'Light_Intensity'] = np.nan

    return df

def main():
    print("--- 1. Data Preparation ---")
    df = generate_synthetic_data()
    print("Initial Data Shape:", df.shape)

    # Missing value handling
    print("Missing values before imputation:\n", df.isnull().sum())
    imputer = SimpleImputer(strategy='median')
    df['Light_Intensity'] = imputer.fit_transform(df[['Light_Intensity']])
    print("Missing values after imputation:\n", df.isnull().sum())

    print("\n--- 2. Feature Engineering & EDA ---")
    # Interaction Feature: Light * Humidity
    df['Light_x_Humidity'] = df['Light_Intensity'] * df['Humidity']

    X = df.drop('Current_Density', axis=1)
    y = df['Current_Density']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # EDA: Correlation Heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Correlation Heatmap")
    plt.savefig('correlation_heatmap.png')
    plt.close()
    print("Saved 'correlation_heatmap.png'")

    print("\n--- 3. Model Development & 4. Evaluation ---")

    def evaluate_model(model, X_t, y_t, name="Model"):
        preds = model.predict(X_t)
        rmse = np.sqrt(mean_squared_error(y_t, preds))
        mae = mean_absolute_error(y_t, preds)
        r2 = r2_score(y_t, preds)
        print(f"[{name}] RMSE: {rmse:.4f} | MAE: {mae:.4f} | R2: {r2:.4f}")
        return preds, rmse, mae, r2

    # Linear Regression
    lr_model = LinearRegression()
    lr_model.fit(X_train_scaled, y_train)
    evaluate_model(lr_model, X_test_scaled, y_test, "Linear Regression")

    # Random Forest Regressor
    rf_model = RandomForestRegressor(random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    evaluate_model(rf_model, X_test_scaled, y_test, "Random Forest")

    # Cross Validation for RF
    cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5, scoring='neg_mean_squared_error')
    print(f"Random Forest 5-Fold CV RMSE: {np.mean(np.sqrt(-cv_scores)):.4f}")

    print("\n--- 5. Optimization (Hyperparameter Tuning) ---")
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [None, 10, 20]
    }
    grid_search = GridSearchCV(RandomForestRegressor(random_state=42), param_grid, cv=3, scoring='r2', n_jobs=-1)
    grid_search.fit(X_train_scaled, y_train)
    best_rf = grid_search.best_estimator_
    print("Best RF Params:", grid_search.best_params_)
    rf_preds, _, _, _ = evaluate_model(best_rf, X_test_scaled, y_test, "Optimized Random Forest")

    print("\n--- 6. Deep Learning Model (Keras) ---")
    # Set random seed for reproducibility
    tf.random.set_seed(42)

    nn_model = Sequential([
        Input(shape=(X_train_scaled.shape[1],)),
        Dense(64, activation='relu'),
        Dense(32, activation='relu'),
        Dense(1)
    ])

    nn_model.compile(optimizer='adam', loss='mse')

    history = nn_model.fit(X_train_scaled, y_train, epochs=50, validation_split=0.2, verbose=0)

    nn_preds = nn_model.predict(X_test_scaled).flatten()
    print("[Neural Network]")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_test, nn_preds)):.4f}")
    print(f"MAE: {mean_absolute_error(y_test, nn_preds):.4f}")
    print(f"R2: {r2_score(y_test, nn_preds):.4f}")

    # Training Plot
    plt.figure(figsize=(8, 6))
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Neural Network Training History')
    plt.xlabel('Epochs')
    plt.ylabel('Loss (MSE)')
    plt.legend()
    plt.savefig('nn_training_history.png')
    plt.close()
    print("Saved 'nn_training_history.png'")

    print("\n--- 7. Visualization & 8. Output ---")
    # Feature Importance (Random Forest)
    plt.figure(figsize=(8, 6))
    sns.barplot(x=best_rf.feature_importances_, y=X.columns)
    plt.title('Feature Importance (Optimized Random Forest)')
    plt.savefig('feature_importance.png')
    plt.close()

    # Prediction vs Actual
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, rf_preds, alpha=0.5)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('Actual Current Density')
    plt.ylabel('Predicted Current Density')
    plt.title('Prediction vs Actual (Optimized RF)')
    plt.savefig('prediction_vs_actual.png')
    plt.close()

    # Residual Plot
    residuals = y_test - rf_preds
    plt.figure(figsize=(8, 6))
    sns.histplot(residuals, kde=True)
    plt.title('Residuals Distribution (Optimized RF)')
    plt.xlabel('Residuals')
    plt.savefig('residuals_plot.png')
    plt.close()
    print("Saved evaluation plots.")

    print("\n--- Bonus: Save Model & Prediction Function ---")
    # Save the best machine learning model
    joblib.dump(best_rf, 'best_rf_model.pkl')
    # Save scaler
    joblib.dump(scaler, 'scaler.pkl')
    print("Model and Scaler saved successfully.")

    def predict_new_input(light, humidity, bacteria):
        # Calculate interaction
        interaction = light * humidity
        input_data = pd.DataFrame([[light, humidity, bacteria, interaction]],
                                  columns=['Light_Intensity', 'Humidity', 'Bacterial_Density', 'Light_x_Humidity'])
        scaled_input = scaler.transform(input_data)
        pred = best_rf.predict(scaled_input)
        return pred[0]

    sample_light = 5000
    sample_humidity = 65
    sample_bacteria = 1.0
    print(f"\nTesting Prediction Function:")
    print(f"Inputs -> Light: {sample_light}, Humidity: {sample_humidity}, Bacteria: {sample_bacteria}")
    print(f"Predicted Current Density: {predict_new_input(sample_light, sample_humidity, sample_bacteria):.2f} mA/m^2")

if __name__ == "__main__":
    main()
