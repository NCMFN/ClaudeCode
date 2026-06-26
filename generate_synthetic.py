import pandas as pd
import numpy as np

np.random.seed(42)
n_samples = 1000

data = {
    'wall_type': np.random.choice(['Mud', 'Brick', 'Concrete', 'Wood'], n_samples),
    'roof_type': np.random.choice(['Thatch', 'Iron Sheet', 'Tile', 'Concrete'], n_samples),
    'bed_net_available': np.random.choice([0, 1], n_samples),
    'bed_net_used_last_night': np.random.choice([0, 1], n_samples),
    'proximity_water_body_m': np.random.uniform(0, 2000, n_samples),
    'household_size': np.random.randint(1, 16, n_samples),
    'education_head': np.random.choice(['None', 'Primary', 'Secondary', 'Tertiary'], n_samples),
    'income_level': np.random.choice(['Low', 'Middle', 'High'], n_samples),
    'eave_open': np.random.choice([0, 1], n_samples),
    'floor_type': np.random.choice(['Earth', 'Cement', 'Tile'], n_samples),
    'num_windows_screened': np.random.randint(0, 7, n_samples)
}

df = pd.DataFrame(data)

# Simulate target using logistic probabilities
logits = (
    (df['wall_type'] == 'Mud') * 1.5 -
    (df['wall_type'] == 'Concrete') * 1.0 +
    (df['roof_type'] == 'Thatch') * 1.2 -
    (df['bed_net_used_last_night'] * 2.0) -
    (df['bed_net_available'] * 0.5) +
    ((2000 - df['proximity_water_body_m']) / 1000.0) * 1.5 +
    df['household_size'] * 0.1 -
    (df['education_head'] == 'Tertiary') * 1.0 +
    (df['education_head'] == 'None') * 0.5 -
    (df['income_level'] == 'High') * 1.2 +
    (df['income_level'] == 'Low') * 0.8 +
    df['eave_open'] * 1.0 +
    (df['floor_type'] == 'Earth') * 1.2 -
    df['num_windows_screened'] * 0.3 -
    2.0 # bias
)

probs = 1 / (1 + np.exp(-logits))
df['target'] = np.random.binomial(1, probs)

df.to_csv('malaria_household_risk/data/raw/synthetic_dataset.csv', index=False)
print(df['target'].value_counts())
