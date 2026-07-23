import pandas as pd
import numpy as np
import os

def generate_data(n_samples=3000, random_seed=42):
    """
    Generates synthetic 19th-century submarine telegraph cable fault telemetry.

    Ranges based on historical data for 1858-1866 transatlantic cables.
    - Resistance R (Ohm/mi): 2.5 - 12.0
    - Capacitance C (uF/mi): 0.25 - 0.45
    - Voltage V (VDC): 12 - 700 (12V typical, 700V Whitehouse coil)
    - Length L (nmi): 500 - 2200
    - Signal Retardation t (ms): proportional to R * C * L^2 (Kelvin's Law of Squares)

    Classes:
    0: Insulation Degradation
    1: Inductive Crosstalk
    2: Ground Faults & Leakage
    """
    np.random.seed(random_seed)

    # Generate independent features
    # V is bimodal: mostly low voltage (12-50V), some high voltage tests (500-700V)
    v_low = np.random.uniform(12, 50, int(n_samples * 0.8))
    v_high = np.random.uniform(500, 700, int(n_samples * 0.2))
    v = np.concatenate([v_low, v_high])
    np.random.shuffle(v)

    r = np.random.uniform(2.5, 12.0, n_samples)
    c = np.random.uniform(0.25, 0.45, n_samples)
    l = np.random.uniform(500, 2200, n_samples)

    # Latent variables
    insulation_thickness = np.random.uniform(0.1, 0.5, n_samples) # proxy
    parallel_path_proxy = np.random.uniform(0, 1, n_samples)
    seawater_exposure = np.random.uniform(0, 1, n_samples)

    # Calculate retardation t (ms) based on Kelvin's Law of Squares
    # t ~ R * C * L^2. We add some noise.
    # Scale factor to put it in 100-1800 ms range
    base_t = r * c * (l ** 2)
    # Normalize and scale
    t_min, t_max = 100, 1800
    t = (base_t - base_t.min()) / (base_t.max() - base_t.min()) * (t_max - t_min) + t_min
    t += np.random.normal(0, 50, n_samples) # Add noise
    t = np.clip(t, 50, 2500)

    # Calculate fault probabilities
    # 0: Insulation Degradation (High V, High C, Thin Insulation)
    prob_0 = (v / 700) * 0.5 + (c / 0.45) * 0.3 + ((0.5 - insulation_thickness) / 0.4) * 0.2

    # 1: Inductive Crosstalk (Parallel path, moderate R)
    prob_1 = parallel_path_proxy * 0.6 + (r > 5) * (r < 9) * 0.4

    # 2: Ground Faults & Leakage (Low R (proxy for insulation resistance here), High seawater exposure)
    prob_2 = ((12.0 - r) / 9.5) * 0.4 + seawater_exposure * 0.6

    # Add some base rates to achieve ~75% in classes 0 and 2
    prob_0 *= 1.5
    prob_2 *= 1.2
    prob_1 *= 0.5

    probs = np.vstack([prob_0, prob_1, prob_2]).T

    # Add random noise to probs
    probs += np.random.normal(0, 0.1, probs.shape)
    probs = np.clip(probs, 0.01, None) # avoid negative probabilities

    # Normalize probabilities
    probs = probs / probs.sum(axis=1, keepdims=True)

    # Assign labels based on probabilities
    labels = [np.random.choice([0, 1, 2], p=p) for p in probs]

    # Map back to string labels for clarity, we can encode them later if needed
    label_map = {
        0: 'Insulation Degradation',
        1: 'Inductive Crosstalk',
        2: 'Ground Faults & Leakage'
    }

    df = pd.DataFrame({
        'resistance_ohm_per_mi': r,
        'capacitance_uf_per_mi': c,
        'voltage_vdc': v,
        'length_nmi': l,
        'retardation_ms': t,
        'fault_class': [label_map[y] for y in labels]
    })

    # Introduce missingness (realistic for 19th-century logbooks)
    # 5% missingness in resistance and capacitance
    missing_mask_r = np.random.rand(n_samples) < 0.05
    missing_mask_c = np.random.rand(n_samples) < 0.05
    missing_mask_t = np.random.rand(n_samples) < 0.10

    df.loc[missing_mask_r, 'resistance_ohm_per_mi'] = np.nan
    df.loc[missing_mask_c, 'capacitance_uf_per_mi'] = np.nan
    df.loc[missing_mask_t, 'retardation_ms'] = np.nan

    return df

if __name__ == '__main__':
    print("Generating synthetic 19th-century submarine telegraph cable fault telemetry...")
    df = generate_data()
    output_path = os.path.join(os.path.dirname(__file__), 'telegraph_faults.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset generated successfully at {output_path} with {len(df)} rows.")
    print("Class distribution:")
    print(df['fault_class'].value_counts(normalize=True))
