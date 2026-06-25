import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as plt_sns
import seaborn as sns
import os
from matplotlib.patches import FancyBboxPatch
import scipy.stats as stats

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def phase2_eda(df, out_fig_dir, out_tab_dir):
    # Step 2.1 - Satiety Index Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x='Satiety_Index', hue='Category', multiple='stack', bins=20, ax=ax)
    ax.set_title('Satiety Index Distribution by Category')

    # highlight boiled potatoes
    potato = df[df['Food'].str.contains('potato', case=False, na=False)].head(1)
    if not potato.empty:
        si_potato = potato['Satiety_Index'].values[0]
        ax.annotate('Boiled Potatoes (SI ≈ 323%)', xy=(si_potato, 0), xytext=(si_potato, 5),
                    arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='center', verticalalignment='top')

    plt.tight_layout()
    plt.savefig(os.path.join(out_fig_dir, 'fig1_si_distribution.png'))
    plt.close()

    # Step 2.2 - The Potato Paradox (GI vs Satiety Index)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x='GI_value', y='Satiety_Index', hue='Category', ax=ax)

    ax.axvline(70, color='r', linestyle='--', alpha=0.5, label='High GI threshold (70)')
    ax.axhline(100, color='g', linestyle='--', alpha=0.5, label='White Bread Baseline (100)')

    # annotate key outliers
    outliers = df[df['Food'].str.contains('potato|bread, white|fish', case=False, na=False)]
    for _, row in outliers.iterrows():
        ax.annotate(row['Food'], (row['GI_value'], row['Satiety_Index']))

    ax.set_title('The Potato Paradox: GI vs. Satiety Index')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(out_fig_dir, 'fig2_gi_vs_si_scatter.png'))
    plt.close()

    # Step 2.3 - Feature Correlation Matrix
    if 'GL' not in df.columns:
        # compute GL for correlation if not present yet
        df['Avail_Carb'] = df['Carbohydrate_g'] - df['Fiber_g']
        df['Avail_Carb'] = df['Avail_Carb'].clip(lower=0)
        df['GL'] = (df['GI_value'] * df['Avail_Carb']) / 100

    corr_cols = ['Fiber_g', 'Water_g', 'Protein_g', 'Carbohydrate_g', 'Fat_g', 'Energy_kcal', 'GL', 'Satiety_Index']
    corr_df = df[corr_cols]

    pearson_corr = corr_df.corr(method='pearson')
    spearman_corr = corr_df.corr(method='spearman')

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pearson_corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax)
    ax.set_title('Pearson Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(os.path.join(out_fig_dir, 'fig3_correlation_heatmap.png'))
    plt.close()

    # Save correlation table
    pearson_corr.to_csv(os.path.join(out_tab_dir, 'table1_correlations.csv'))

    # Step 2.4 - Per-category Box Plots
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x='Category', y='Satiety_Index', ax=ax, color='lightgray', showfliers=False)
    sns.stripplot(data=df, x='Category', y='Satiety_Index', hue='Category', ax=ax, alpha=0.7, jitter=True, legend=False)
    ax.set_title('Satiety Index by Food Category')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(out_fig_dir, 'fig4_si_by_category.png'))
    plt.close()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, 'data', 'processed')
    out_fig_dir = os.path.join(base_dir, 'outputs', 'figures')
    out_tab_dir = os.path.join(base_dir, 'outputs', 'tables')

    df = pd.read_csv(os.path.join(proc_dir, 'satiety_features.csv'))
    phase2_eda(df, out_fig_dir, out_tab_dir)

if __name__ == "__main__":
    main()
