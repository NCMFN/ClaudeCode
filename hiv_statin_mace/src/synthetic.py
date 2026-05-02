import numpy as np
import pandas as pd

def generate_synthetic_data(n_samples=5000, random_seed=42):
    """
    Generate synthetic data resembling HIV+ patients from REPRIEVE.
    """
    np.random.seed(random_seed)

    # 1. Generate core features
    age = np.clip(np.random.normal(47, 8, n_samples), 18, 70)
    sex_at_birth = np.random.choice([0, 1], size=n_samples, p=[0.2, 0.8]) # majority male in typical HIV cohorts

    cd4_count_nadir = np.random.lognormal(5.5, 0.5, n_samples)
    cd4_cd8_ratio = np.random.uniform(0.2, 1.8, n_samples)
    viral_load_suppressed = np.random.binomial(1, 0.85, n_samples)
    art_duration_years = np.random.uniform(1, 25, n_samples)

    # ART Regimen class
    art_classes = ['NRTI', 'NNRTI', 'PI', 'INSTI']
    art_choices = np.random.choice(art_classes, size=n_samples)

    il6_level = np.random.lognormal(1.0, 0.7, n_samples)
    hscrp_level = np.random.lognormal(0.5, 0.8, n_samples)

    non_hdl_cholesterol = np.random.normal(145, 30, n_samples)
    systolic_bp = np.random.normal(128, 16, n_samples)

    smoking_status = np.random.choice(['never', 'former', 'current'], size=n_samples, p=[0.4, 0.3, 0.3])
    diabetes_status = np.random.binomial(1, 0.1, n_samples)
    bmi = np.random.normal(25, 4, n_samples)

    # Missing values injection (from preprocess step: IL-6 and hsCRP might be missing > 30%)
    il6_level_missing = np.where(np.random.rand(n_samples) < 0.35, np.nan, il6_level)
    hscrp_level_missing = np.where(np.random.rand(n_samples) < 0.35, np.nan, hscrp_level)

    # DataFrame creation
    df = pd.DataFrame({
        'age': age,
        'sex_at_birth': sex_at_birth,
        'cd4_count_nadir': cd4_count_nadir,
        'cd4_cd8_ratio': cd4_cd8_ratio,
        'viral_load_suppressed': viral_load_suppressed,
        'art_duration_years': art_duration_years,
        'art_regimen_class': art_choices,
        'il6_level': il6_level_missing,
        'hscrp_level': hscrp_level_missing,
        'non_hdl_cholesterol': non_hdl_cholesterol,
        'systolic_bp': systolic_bp,
        'smoking_status': smoking_status,
        'diabetes_status': diabetes_status,
        'bmi': bmi
    })

    # One-hot encoding for art_regimen_class to make it ready
    df = pd.get_dummies(df, columns=['art_regimen_class'])

    # Needs some other fields for Framingham/ASCVD (impute reasonable values if not explicitly requested to generate)
    df['total_cholesterol'] = df['non_hdl_cholesterol'] + np.random.normal(45, 10, n_samples)
    df['hdl_cholesterol'] = df['total_cholesterol'] - df['non_hdl_cholesterol']
    df['bp_treatment'] = np.random.binomial(1, 0.15, n_samples)
    df['race'] = np.random.choice(['White', 'African American', 'Other'], size=n_samples, p=[0.5, 0.4, 0.1])


    # Target Variable Simulation
    # Base probability 0.08, elevated to 0.18 for hscrp > 4, cd4_nadir < 200, or viral_load_suppressed == 0
    base_probs = np.full(n_samples, 0.08)
    elevated_condition = (hscrp_level > 4) | (cd4_count_nadir < 200) | (viral_load_suppressed == 0)
    base_probs[elevated_condition] = 0.18

    mace = np.random.binomial(1, base_probs)
    df['MACE'] = mace
    df['is_synthetic'] = True

    return df

if __name__ == '__main__':
    df = generate_synthetic_data()
    df.to_csv('../data/processed/synthetic_data.csv', index=False)
    print("Synthetic dataset generated: ../data/processed/synthetic_data.csv")
