import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import average_precision_score

RANDOM_SEED = 42

def test_adversarial(df, splits):
    train = splits['group']['train']
    test = splits['group']['test']

    features = ['hour_cos', 'hour_sin', 'day_of_week', 'event_count', 'graph_degree', 'graph_betweenness', 'peer_z_score']

    model = XGBClassifier(random_state=RANDOM_SEED, eval_metric='logloss')
    model.fit(train[features], train['label'])

    # Baseline
    probs = model.predict_proba(test[features])[:, 1]
    baseline_prauc = average_precision_score(test['label'], probs)
    baseline_preds = model.predict(test[features])

    results = []

    # 1. Existing Evasion Attack (Perturbs non-temporal features like peer_z_score, graph_degree)
    X_evasion = test[features].copy()
    X_evasion['peer_z_score'] = X_evasion['peer_z_score'] * 1.5
    X_evasion['graph_degree'] = X_evasion['graph_degree'] * 1.2
    evasion_probs = model.predict_proba(X_evasion)[:, 1]
    evasion_preds = model.predict(X_evasion)
    results.append({
        'Attack': 'Feature Evasion (Existing)',
        'Features_Perturbed': 'peer_z_score, graph_degree',
        'Touches_hour_cos': False,
        'Perturbation_Magnitude': '1.2x to 1.5x (Large for graph)',
        'Boundary_Crossing_Fraction': np.mean(evasion_preds != baseline_preds),
        'Resulting_PRAUC': average_precision_score(test['label'], evasion_probs)
    })

    # 2. Existing Label Poisoning (Flip 5% of training labels)
    y_poison = train['label'].copy()
    flip_idx = np.random.choice(len(y_poison), size=int(0.05 * len(y_poison)), replace=False)
    y_poison.iloc[flip_idx] = 1 - y_poison.iloc[flip_idx]

    poison_model = XGBClassifier(random_state=RANDOM_SEED, eval_metric='logloss')
    poison_model.fit(train[features], y_poison)
    poison_probs = poison_model.predict_proba(test[features])[:, 1]
    poison_preds = poison_model.predict(test[features])
    results.append({
        'Attack': 'Label Poisoning 5% (Existing)',
        'Features_Perturbed': 'None (Labels only)',
        'Touches_hour_cos': False,
        'Perturbation_Magnitude': '5% of labels',
        'Boundary_Crossing_Fraction': np.mean(poison_preds != baseline_preds),
        'Resulting_PRAUC': average_precision_score(test['label'], poison_probs)
    })

    # 3. New Attack: hour_cos Perturbation
    X_time = test[features].copy()
    # Shift time by 12 hours (cos shift: cos(theta + pi) = -cos(theta))
    X_time['hour_cos'] = -X_time['hour_cos']
    X_time['hour_sin'] = -X_time['hour_sin']

    time_probs = model.predict_proba(X_time)[:, 1]
    time_preds = model.predict(X_time)
    results.append({
        'Attack': 'Temporal Shift (New)',
        'Features_Perturbed': 'hour_cos, hour_sin',
        'Touches_hour_cos': True,
        'Perturbation_Magnitude': '12 hours (Full range shift)',
        'Boundary_Crossing_Fraction': np.mean(time_preds != baseline_preds),
        'Resulting_PRAUC': average_precision_score(test['label'], time_probs)
    })

    return pd.DataFrame(results)

if __name__ == "__main__":
    from phase1_ingestion import ingest_data
    from phase2_features import engineer_features
    from phase3_modeling import split_data

    df = engineer_features(ingest_data())
    splits = split_data(df)

    res = test_adversarial(df, splits)
    res.to_csv("outputs/tables/adversarial_diagnostics.csv", index=False)
    print("Phase 4 complete.")
