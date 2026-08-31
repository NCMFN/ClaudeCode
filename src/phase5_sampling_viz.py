import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

STYLE = {'primary': '#2E5EAA', 'secondary': '#D9534F'}

def generate_sampling_artifacts(df, splits):
    # 1. Period bucket counts
    n = len(df)
    train_end = int(n * 0.6)
    val_end = int(n * 0.8)

    df['period'] = 'test'
    df.loc[:val_end, 'period'] = 'val'
    df.loc[:train_end, 'period'] = 'train'

    period_counts = df.groupby(['period', 'label']).size().unstack(fill_value=0)
    period_counts.columns = ['Benign', 'Malicious']
    period_counts['Ratio (Malicious/Benign)'] = period_counts['Malicious'] / period_counts['Benign']
    period_counts.to_csv("outputs/tables/sampling_period_counts.csv")

    # 2. Temporal overlap table
    mal_min, mal_max = df[df['label']==1]['timestamp'].min(), df[df['label']==1]['timestamp'].max()
    ben_min, ben_max = df[df['label']==0]['timestamp'].min(), df[df['label']==0]['timestamp'].max()
    overlap = pd.DataFrame([
        {'Class': 'Malicious', 'Start': mal_min, 'End': mal_max},
        {'Class': 'Benign', 'Start': ben_min, 'End': ben_max}
    ])
    overlap.to_csv("outputs/tables/sampling_temporal_overlap.csv", index=False)

    # 3. Temporal distribution figure (stacked timeline)
    plt.figure(figsize=(10, 6))
    plt.hist([df[df['label']==0]['timestamp'], df[df['label']==1]['timestamp']],
             bins=50, stacked=True, color=[STYLE['primary'], STYLE['secondary']],
             label=['Benign', 'Malicious'])
    plt.title("Temporal Distribution of Events")
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig("outputs/figures/temporal_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 4. hour_cos distribution
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=df[df['label']==0]['hour_cos'], color=STYLE['primary'], label='Benign', fill=True)
    sns.kdeplot(data=df[df['label']==1]['hour_cos'], color=STYLE['secondary'], label='Malicious', fill=True)
    plt.title("Distribution of hour_cos (Temporal Shortcut)")
    plt.xlabel("hour_cos")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig("outputs/figures/hour_cos_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 5. day_of_week distribution
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='day_of_week', hue='label', palette=[STYLE['primary'], STYLE['secondary']])
    plt.title("Day of Week Distribution by Class")
    plt.xlabel("Day of Week (0=Mon, 6=Sun)")
    plt.ylabel("Count")
    plt.legend(title='Label', labels=['Benign', 'Malicious'])
    plt.tight_layout()
    plt.savefig("outputs/figures/day_of_week_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()

def generate_ablation_chart(ablation_df):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=ablation_df, x='Split', y='PR-AUC', hue='Variant', palette='viridis')
    plt.title("Feature Ablation Study (PR-AUC across Evaluation Modes)")
    plt.xlabel("Evaluation Split Mode")
    plt.ylabel("PR-AUC")
    plt.ylim(0, 1.05)
    plt.legend(title="Feature Variant", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("outputs/figures/ablation_chart.png", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    from phase1_ingestion import ingest_data
    from phase2_features import engineer_features
    from phase3_modeling import split_data

    df = engineer_features(ingest_data())
    splits = split_data(df)
    generate_sampling_artifacts(df, splits)
    print("Phase 5 complete.")
