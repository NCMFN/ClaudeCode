from src.data_loader import download_data, load_all_datasets
from src.eda import run_eda
from src.feature_engineering import engineer_features
from src.preprocessing import preprocess_data
from src.train import train_and_evaluate
from src.tune import tune_xgboost
from src.interpret import run_interpretation
from src.simulate import run_simulation, run_trend_analysis
from src.report import generate_report
import joblib

def run_pipeline():
    print("=== Step 1: Downloading & Loading Data ===")
    p_path, w_path, l_path = download_data()
    df = load_all_datasets(p_path, w_path, l_path)

    print("\n=== Step 2: EDA ===")
    run_eda(df, "results/figures")

    print("\n=== Step 3: Feature Engineering ===")
    df = engineer_features(df)

    print("\n=== Step 4: Preprocessing ===")
    X_train, X_val, X_test, y_train, y_val, y_test, features = preprocess_data(df)

    print("\n=== Step 5: Model Training & Evaluation ===")
    train_and_evaluate(X_train, y_train, X_val, y_val)

    print("\n=== Step 6: Hyperparameter Tuning ===")
    best_model = tune_xgboost(X_train, y_train, X_test, y_test)

    print("\n=== Step 7: Interpretability & Analysis ===")
    run_interpretation(best_model, X_train)

    print("\n=== Step 8 & 9: Simulation and Trend Analysis ===")
    scaler = joblib.load('results/models/scaler.pkl')
    run_simulation(df, best_model, scaler)
    run_trend_analysis(df, best_model, scaler)

    print("\n=== Step 10: Generating Report ===")
    # Patch report.py slightly to use load_all_datasets but it's simpler to just call it.
    generate_report()

    print("\nPipeline Complete!")

if __name__ == "__main__":
    run_pipeline()
