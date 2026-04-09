import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from xgboost import XGBRegressor, XGBClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, f1_score, roc_auc_score
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns
import shap

# --- Data Generation / Simulation (Mocking the specified datasets) ---
def generate_mock_data(n_samples=2000):
    np.random.seed(42)

    # 1. Plant Features (X1) - Mocking TRY, NCBI GEO, GBIF
    plant_data = pd.DataFrame({
        'species_id': np.random.randint(1, 100, n_samples),
        'root_depth_cm': np.random.normal(50, 15, n_samples),
        'growth_rate': np.random.normal(2, 0.5, n_samples),
        'geo_lat': np.random.uniform(-90, 90, n_samples),
        'geo_lon': np.random.uniform(-180, 180, n_samples),
        'gene_expr_pc1': np.random.normal(0, 1, n_samples),
        'gene_expr_pc2': np.random.normal(0, 1, n_samples)
    })

    # 2. Soil Features (X2) - Mocking LUCAS, SoilGrids, USDA NRCS
    soil_data = pd.DataFrame({
        'soil_pH': np.random.normal(6.5, 1.0, n_samples),
        'soil_cec': np.random.normal(20, 5, n_samples), # Cation Exchange Capacity
        'clay_percent': np.random.uniform(10, 50, n_samples),
        'organic_matter_percent': np.random.uniform(1, 10, n_samples),
        'baseline_metal_conc': np.random.lognormal(2, 0.5, n_samples)
    })

    # 3. Contaminant Features (X3) - Mocking PubChem, FOREGS, EPA
    contaminants = ['Lead', 'Cadmium', 'Arsenic', 'Zinc', 'Copper', 'PCE', 'TCE']
    contaminant_data = pd.DataFrame({
        'contaminant_name': np.random.choice(contaminants, n_samples),
        'molecular_weight': np.random.uniform(50, 300, n_samples),
        'log_kow': np.random.normal(2, 1, n_samples), # Octanol-water partition coefficient
        'solubility_mg_L': np.random.lognormal(3, 1, n_samples)
    })

    # 4. Climate Features (X4) - Mocking WorldClim, OpenLandMap
    climate_data = pd.DataFrame({
        'mean_annual_temp_c': np.random.normal(15, 8, n_samples),
        'annual_precip_mm': np.random.normal(800, 300, n_samples),
        'ndvi': np.random.uniform(0.1, 0.9, n_samples)
    })

    # Combine features
    df = pd.concat([plant_data, soil_data, contaminant_data, climate_data], axis=1)

    # 5. Target Variables - Mocking PhytoRem, HyperAccumulator DB, EPA DB

    # Simulate BCF (Bioconcentration Factor) based on features
    # Higher CEC -> lower bioavailability -> lower BCF
    # Certain contaminants (e.g., Cd) tend to have higher BCF
    base_bcf = 100 + df['root_depth_cm']*0.5 - df['soil_pH']*5 + df['annual_precip_mm']*0.01
    contaminant_multiplier = np.where(df['contaminant_name'] == 'Cadmium', 1.5, 1.0)
    df['target_bcf'] = np.maximum(0, base_bcf * contaminant_multiplier + np.random.normal(0, 20, n_samples))

    # Simulate TF (Translocation Factor)
    df['target_tf'] = np.maximum(0, 0.5 + df['gene_expr_pc1']*0.1 + np.random.normal(0, 0.2, n_samples))

    # Simulate Remediation Efficiency (%)
    efficiency = df['target_bcf'] * df['target_tf'] / 100 + df['growth_rate'] * 5
    df['target_efficiency'] = np.clip(efficiency + np.random.normal(0, 5, n_samples), 0, 100)

    # Simulate High Affinity / Hyperaccumulator Class (Binary)
    # E.g., BCF > 100 and TF > 1 -> Class 1
    df['target_high_affinity'] = ((df['target_bcf'] > 120) & (df['target_tf'] > 0.8)).astype(int)

    return df

# --- Data Preprocessing ---
def preprocess_data(df):
    """Cleans, normalizes, and encodes the dataset."""
    print("Preprocessing data...")

    # Separate features and targets
    targets = ['target_bcf', 'target_tf', 'target_efficiency', 'target_high_affinity']
    y = df[targets]
    X = df.drop(columns=targets)

    # Define feature groups based on the instructions
    plant_cols = ['root_depth_cm', 'growth_rate', 'geo_lat', 'geo_lon', 'gene_expr_pc1', 'gene_expr_pc2']
    soil_cols = ['soil_pH', 'soil_cec', 'clay_percent', 'organic_matter_percent', 'baseline_metal_conc']
    contaminant_cols = ['molecular_weight', 'log_kow', 'solubility_mg_L'] # Excluding categorical for now
    climate_cols = ['mean_annual_temp_c', 'annual_precip_mm', 'ndvi']
    categorical_cols = ['contaminant_name', 'species_id']

    # Handling categorical: One-hot encoding for simplicity here
    X = pd.get_dummies(X, columns=['contaminant_name'], drop_first=True)
    contaminant_encoded_cols = [c for c in X.columns if c.startswith('contaminant_name_')]
    contaminant_cols.extend(contaminant_encoded_cols)

    X = X.drop('species_id', axis=1) # Drop species ID or embed it; dropping for simplicity in this baseline

    # Impute missing values (if any were present)
    imputer = SimpleImputer(strategy='mean')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)

    # Normalize numeric features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_imputed), columns=X_imputed.columns)

    # Group features for multi-input network
    X_grouped = {
        'plant': X_scaled[plant_cols].values,
        'soil': X_scaled[soil_cols].values,
        'contaminant': X_scaled[contaminant_cols].values,
        'climate': X_scaled[climate_cols].values
    }

    return X_grouped, X_scaled, y, plant_cols, soil_cols, contaminant_cols, climate_cols

# --- Model Architectures ---

def build_multi_modal_nn(input_shapes):
    """Builds the multi-input neural network with regression and classification heads."""
    print("Building Multi-Modal Neural Network...")

    # Inputs
    input_plant = keras.Input(shape=(input_shapes['plant'],), name='plant_input')
    input_soil = keras.Input(shape=(input_shapes['soil'],), name='soil_input')
    input_contaminant = keras.Input(shape=(input_shapes['contaminant'],), name='contaminant_input')
    input_climate = keras.Input(shape=(input_shapes['climate'],), name='climate_input')

    # Branch representations
    x_plant = layers.Dense(32, activation='relu')(input_plant)
    x_plant = layers.Dropout(0.2)(x_plant)

    x_soil = layers.Dense(32, activation='relu')(input_soil)
    x_soil = layers.Dropout(0.2)(x_soil)

    x_contaminant = layers.Dense(32, activation='relu')(input_contaminant)
    x_contaminant = layers.Dropout(0.2)(x_contaminant)

    x_climate = layers.Dense(16, activation='relu')(input_climate)

    # Fusion layer
    merged = layers.Concatenate()([x_plant, x_soil, x_contaminant, x_climate])
    shared = layers.Dense(64, activation='relu')(merged)
    shared = layers.Dropout(0.3)(shared)
    shared = layers.Dense(32, activation='relu')(shared)

    # Output Heads

    # Regression Head (predicting BCF, TF, Efficiency)
    out_reg = layers.Dense(3, name='regression_head')(shared)

    # Classification Head (predicting High Affinity)
    out_cls = layers.Dense(1, activation='sigmoid', name='classification_head')(shared)

    model = Model(
        inputs=[input_plant, input_soil, input_contaminant, input_climate],
        outputs=[out_reg, out_cls]
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss={
            'regression_head': 'mse',
            'classification_head': 'binary_crossentropy'
        },
        loss_weights={
            'regression_head': 1.0,
            'classification_head': 0.5 # Give slightly less weight to class if desired
        },
        metrics={
            'regression_head': [keras.metrics.RootMeanSquaredError(name='rmse')],
            'classification_head': ['accuracy', keras.metrics.AUC(name='auc')]
        }
    )

    return model

def train_and_evaluate(X_grouped, X_flat, y, input_shapes):
    """Trains baselines and the neural network."""

    # Split targets
    y_reg = y[['target_bcf', 'target_tf', 'target_efficiency']].values
    y_cls = y['target_high_affinity'].values

    # Train/test split (using flat X for indices to split grouped X identically)
    X_train_flat, X_test_flat, y_reg_train, y_reg_test, y_cls_train, y_cls_test, indices_train, indices_test = train_test_split(
        X_flat, y_reg, y_cls, np.arange(len(X_flat)), test_size=0.2, random_state=42, stratify=y_cls
    )

    X_train_grouped = {k: v[indices_train] for k, v in X_grouped.items()}
    X_test_grouped = {k: v[indices_test] for k, v in X_grouped.items()}

    # --- Baseline 1: Random Forest (for Efficiency Regression) ---
    print("\nTraining Baseline: Random Forest (Regression - Efficiency)")
    rf_reg = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_reg.fit(X_train_flat, y_reg_train[:, 2]) # Predicting efficiency
    rf_pred = rf_reg.predict(X_test_flat)
    print(f"RF RMSE: {mean_squared_error(y_reg_test[:, 2], rf_pred, squared=False):.4f}")
    print(f"RF R2: {r2_score(y_reg_test[:, 2], rf_pred):.4f}")

    # --- Baseline 2: XGBoost (for High Affinity Classification) ---
    print("\nTraining Baseline: XGBoost (Classification - High Affinity)")
    xgb_cls = XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
    xgb_cls.fit(X_train_flat, y_cls_train)
    xgb_pred = xgb_cls.predict(X_test_flat)
    xgb_prob = xgb_cls.predict_proba(X_test_flat)[:, 1]
    print(f"XGB Accuracy: {accuracy_score(y_cls_test, xgb_pred):.4f}")
    print(f"XGB F1: {f1_score(y_cls_test, xgb_pred):.4f}")
    print(f"XGB ROC-AUC: {roc_auc_score(y_cls_test, xgb_prob):.4f}")

    # --- Deep Learning: Multi-Modal NN ---
    print("\nTraining Multi-Modal Neural Network...")
    nn_model = build_multi_modal_nn(input_shapes)

    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss', patience=10, restore_best_weights=True
    )

    history = nn_model.fit(
        {
            'plant_input': X_train_grouped['plant'],
            'soil_input': X_train_grouped['soil'],
            'contaminant_input': X_train_grouped['contaminant'],
            'climate_input': X_train_grouped['climate']
        },
        {
            'regression_head': y_reg_train,
            'classification_head': y_cls_train
        },
        validation_split=0.2,
        epochs=50,
        batch_size=32,
        callbacks=[early_stopping],
        verbose=0
    )

    print("\nEvaluating NN on Test Set:")
    results = nn_model.evaluate(
        {
            'plant_input': X_test_grouped['plant'],
            'soil_input': X_test_grouped['soil'],
            'contaminant_input': X_test_grouped['contaminant'],
            'climate_input': X_test_grouped['climate']
        },
        {
            'regression_head': y_reg_test,
            'classification_head': y_cls_test
        },
        verbose=0
    )

    # Map metrics
    print(f"Total Loss: {results[0]:.4f}")
    print(f"Regression Loss (MSE): {results[1]:.4f}")
    print(f"Classification Loss (BCE): {results[2]:.4f}")
    print(f"Classification Accuracy: {results[3]:.4f}")
    print(f"Classification AUC: {results[4]:.4f}")
    print(f"Regression RMSE: {results[5]:.4f}")

    # Feature Importance / SHAP (using XGBoost as proxy for feature importance plot)
    plot_feature_importance(xgb_cls, X_flat.columns)
    plot_training_history(history)
    plot_correlation(X_flat)

    # Save Model
    nn_model.save('phytoremediation_multimodal_model.h5')
    print("\nModel saved to 'phytoremediation_multimodal_model.h5'")

def plot_feature_importance(model, feature_names):
    plt.figure(figsize=(10, 8))
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:15] # Top 15
    plt.title('Top 15 Feature Importances (XGBoost Classifier)')
    plt.bar(range(15), importances[indices], align='center')
    plt.xticks(range(15), [feature_names[i] for i in indices], rotation=90)
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    print("Saved feature_importance.png")

def plot_training_history(history):
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 2, 1)
    plt.plot(history.history['regression_head_rmse'], label='Train RMSE')
    plt.plot(history.history['val_regression_head_rmse'], label='Val RMSE')
    plt.title('Regression Head RMSE')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history['classification_head_auc'], label='Train AUC')
    plt.plot(history.history['val_classification_head_auc'], label='Val AUC')
    plt.title('Classification Head AUC')
    plt.legend()

    plt.tight_layout()
    plt.savefig('training_history.png')
    print("Saved training_history.png")

def plot_correlation(X_flat):
    plt.figure(figsize=(12, 10))
    corr = X_flat.iloc[:, :15].corr() # Plotting subset for visibility
    sns.heatmap(corr, annot=False, cmap='coolwarm')
    plt.title('Feature Correlation Heatmap (Subset)')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png')
    print("Saved correlation_heatmap.png")

if __name__ == "__main__":
    df = generate_mock_data()
    X_grouped, X_flat, y, plant_cols, soil_cols, contaminant_cols, climate_cols = preprocess_data(df)

    input_shapes = {
        'plant': len(plant_cols),
        'soil': len(soil_cols),
        'contaminant': len(contaminant_cols),
        'climate': len(climate_cols)
    }

    train_and_evaluate(X_grouped, X_flat, y, input_shapes)
