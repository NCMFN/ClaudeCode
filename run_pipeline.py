import os
import sys

def main():
    print("--- STARTING PIPELINE ---")

    # 1. Data Loader
    print("\n--- STEP 1: Data Ingestion & EDA ---")
    from src.data_loader import load_data, run_eda
    dfs = load_data()
    run_eda(dfs)

    # 2. Preprocessing
    print("\n--- STEP 2: Preprocessing ---")
    from src.preprocessing import run_preprocessing
    run_preprocessing()

    # 3. Feature Engineering
    print("\n--- STEP 3: Feature Engineering ---")
    from src.feature_engineering import run_feature_engineering
    run_feature_engineering()

    # 4. Model Training
    print("\n--- STEP 4: Model Training ---")
    from src.models import run_training
    # Using smaller trial count for testing if needed, else full 50
    run_training(trials=50)

    # 5. Evaluation & Utils
    print("\n--- STEP 5 & 6: Evaluation and Explainability ---")
    from src.evaluation import run_evaluation
    from src.utils import plot_degradation_trends
    import pandas as pd
    run_evaluation()
    try:
        df = pd.read_parquet('data/processed/train_features.parquet')
        plot_degradation_trends(df)
    except Exception as e:
        print(f"Plotting degradation trends skipped: {e}")

    print("\n--- PIPELINE COMPLETE ---")

    # Generate Summary
    os.makedirs('outputs/results', exist_ok=True)
    with open('outputs/results/PIPELINE_SUMMARY.md', 'w') as f:
        f.write("# Pipeline Summary\n\n")
        f.write("Pipeline execution completed successfully.\n\n")
        f.write("## Dataset Statistics\n")
        f.write("Data loaded via Kaggle fallback mechanism (empty DFs if Kaggle credentials absent).\n\n")
        f.write("## Engineered Features\n")
        f.write("- Stress_Index\n- Duty_Cycle\n- Peak_Excursion\n- Thermal_Delta\n- RUL\n\n")
        f.write("## Final Metric Table\n")
        f.write("Saved to `outputs/results/model_comparison.csv`\n\n")
        f.write("## Top SHAP Features\n")
        f.write("Generated in `outputs/figures/shap_summary.png`\n")

if __name__ == "__main__":
    main()
