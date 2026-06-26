# Household Risk Profiling for Malaria Susceptibility

## Research Context
This repository implements a micro-level epidemiological modeling pipeline for classifying household malaria infection status. Understanding household susceptibility based on structural (e.g., wall/roof type), demographic (e.g., household size), and environmental features is vital for targeted public health interventions. This binary classification model predicts infection risk (Target: 1 = Infected, 0 = Uninfected) using explainable models prioritising high-recall outputs.

## Dataset Source & Features
The project utilizes a synthetic dataset replicating key features from authoritative demographic surveys (like DHS/MIS) after original data proved insufficient or restricted.
The schema includes:
- Structural features: `wall_type`, `roof_type`, `floor_type`, `eave_open`, `num_windows_screened`
- Demographic features: `household_size`, `education_head`, `income_level`
- Prevention & Environment: `bed_net_available`, `bed_net_used_last_night`, `proximity_water_body_m`

## Installation and Execution
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the pipeline sequentially from `src`:
   ```bash
   python src/preprocess.py
   python src/features.py
   python src/train.py
   python src/evaluate.py
   python src/explain.py
   ```

## Results Summary (Hold-out Test Set)
| Model | Accuracy | Precision | Recall | F1 Score |
|---|---|---|---|---|
| Logistic Regression | 0.81 | 0.79 | 0.68 | 0.73 |
| Decision Tree | 0.77 | 0.68 | 0.76 | 0.72 |
| Random Forest | 0.75 | 0.74 | 0.55 | 0.63 |

## Scoring a New Household
To score a new household profile, use the `score_household()` function in `src/train.py`. Example usage:
```python
from train import score_household

new_house = {
    'wall_type': 'Mud',
    'roof_type': 'Thatch',
    'bed_net_available': 0,
    'bed_net_used_last_night': 0,
    'proximity_water_body_m': 500,
    'household_size': 8,
    'education_head': 'None',
    'income_level': 'Low',
    'eave_open': 1,
    'floor_type': 'Earth',
    'num_windows_screened': 0
}

risk = score_household(new_house)
print(risk) # Output: {'predicted_class': 1, 'infection_probability': 0.85, 'risk_tier': 'High'}
```
