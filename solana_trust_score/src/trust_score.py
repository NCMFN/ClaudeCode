import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

class TrustScore:
    THRESHOLDS = {
        'HIGH_RISK':    (0.70, 1.00),   # Trust Score 0-30
        'MEDIUM_RISK':  (0.40, 0.70),   # Trust Score 31-60
        'LOW_RISK':     (0.00, 0.40),   # Trust Score 61-100
    }

    def compute(self, rug_pull_probability: float) -> dict:
        rug_pull_probability = max(0.0, min(1.0, rug_pull_probability))
        trust_score = round((1 - rug_pull_probability) * 100, 2)
        risk_tier = 'UNKNOWN'

        for tier, (lo, hi) in self.THRESHOLDS.items():
            if lo <= rug_pull_probability <= hi:
                risk_tier = tier
                break

        return {
            'trust_score': trust_score,
            'rug_pull_probability': round(rug_pull_probability, 4),
            'risk_tier': risk_tier
        }

def compute_and_save_trust_scores(model, X_test, y_test, output_csv: str, output_fig_dir: str):
    print("Computing Trust Scores...")

    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = model.predict(X_test)

    ts_calculator = TrustScore()
    results = []

    for i, prob in enumerate(y_proba):
        ts_dict = ts_calculator.compute(prob)
        ts_dict['index'] = X_test.index[i]
        ts_dict['true_label'] = int(y_test.iloc[i])
        ts_dict['xgb_prediction'] = int(y_pred[i])
        results.append(ts_dict)

    df_ts = pd.DataFrame(results)

    df_ts = df_ts[['index', 'true_label', 'rug_pull_probability', 'trust_score', 'risk_tier', 'xgb_prediction']]

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_ts.to_csv(output_csv, index=False)
    print(f"Trust Scores saved to {output_csv}")

    os.makedirs(output_fig_dir, exist_ok=True)
    plt.figure(figsize=(10, 6))

    sns.histplot(data=df_ts, x='trust_score', hue='true_label', bins=20, multiple='stack', palette=['#1f77b4', '#d62728'])
    plt.title('Trust Score Distribution by True Label')
    plt.xlabel('Trust Score (0=High Risk, 100=Low Risk)')
    plt.ylabel('Count')

    import matplotlib.patches as mpatches
    legit_patch = mpatches.Patch(color='#1f77b4', label='True Label: Legit (0)')
    rug_patch = mpatches.Patch(color='#d62728', label='True Label: Rug Pull (1)')
    plt.legend(handles=[legit_patch, rug_patch])

    plt.tight_layout()
    plt.savefig(os.path.join(output_fig_dir, 'trust_score_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

    return df_ts

if __name__ == "__main__":
    pass
