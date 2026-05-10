import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set plotting styles
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def perform_eda():
    in_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'engineered_nasa_mdp.csv')
    df = pd.read_csv(in_path, low_memory=False)

    out_dir = os.path.join(os.path.dirname(__file__), '..', 'results', 'eda')
    os.makedirs(out_dir, exist_ok=True)

    # Let's collect McCabe+Halstead features (21 features roughly, as many as available)
    # The primary available features in these combined datasets are:
    mccabe_halstead = ['loc', 'v_g', 'ev_g', 'iv_g', 'n', 'v', 'l', 'd', 'i', 'e', 'b', 't',
                       'locode', 'locomment', 'loblank', 'uniq_op', 'uniq_opnd', 'total_op', 'total_opnd']

    # Ensure they exist in df
    available_features = [f for f in mccabe_halstead if f in df.columns]

    # Ensure numeric
    for f in available_features:
        df[f] = pd.to_numeric(df[f], errors='coerce')

    df_clean = df.dropna(subset=available_features + ['complexity_score']).copy()

    # 1. Correlation heatmap
    plt.figure(figsize=(16, 12))
    corr = df_clean[available_features + ['complexity_score']].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Heatmap of Features vs Complexity Score')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'correlation_heatmap.png'))
    plt.close()

    # 2. Distribution plots for PC1, JM1, KC1
    df_filtered = df_clean[df_clean['source_project'].isin(['pc1', 'jm1', 'kc1'])]
    for feature in ['v_g', 'v', 'loc']:
        plt.figure(figsize=(10, 6))
        sns.violinplot(x='source_project', y=feature, data=df_filtered)
        plt.title(f'Distribution of {feature} across Projects (PC1, JM1, KC1)')
        plt.yscale('log')
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'distribution_{feature}.png'))
        plt.close()

    # 3. Scatter matrix of top-8 correlated features
    top_8 = corr['complexity_score'].abs().sort_values(ascending=False).index[1:9].tolist()
    # sample for scatter matrix to avoid memory issues
    sns.pairplot(df_clean.sample(min(1000, len(df_clean)))[top_8 + ['decomposition_depth']], hue='decomposition_depth', palette='viridis')
    plt.savefig(os.path.join(out_dir, 'scatter_matrix.png'))
    plt.close()

    # 4. Box plots of Halstead Volume (v) and Cyclomatic Complexity v(g) per dataset
    for feature in ['v', 'v_g']:
        plt.figure(figsize=(12, 6))
        sns.boxplot(x='source_project', y=feature, data=df_clean)
        plt.title(f'Box Plot of {feature} per Dataset')
        plt.yscale('log')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f'boxplot_{feature}.png'))
        plt.close()

    # 5. Outlier analysis using IQR
    Q1 = df_clean[available_features].quantile(0.25)
    Q3 = df_clean[available_features].quantile(0.75)
    IQR = Q3 - Q1
    condition = ~((df_clean[available_features] > (Q3 + 3 * IQR)).any(axis=1))
    df_no_outliers = df_clean[condition]
    print(f"Original shape: {df_clean.shape}, Without outliers: {df_no_outliers.shape}")
    # Saving dataset without outliers for training if preferred, or just return
    df_no_outliers.to_csv(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'engineered_nasa_mdp_no_outliers.csv'), index=False)

    # 6. PCA biplot
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    X_scaled = StandardScaler().fit_transform(df_no_outliers[available_features].fillna(0))
    pca = PCA(n_components=3)
    pca_result = pca.fit_transform(X_scaled)

    plt.figure(figsize=(8, 6))
    plt.scatter(pca_result[:, 0], pca_result[:, 1], alpha=0.5, c=df_no_outliers['complexity_score'], cmap='viridis')
    plt.colorbar(label='Complexity Score')
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} var)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} var)')
    plt.title('PCA Biplot')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'pca_biplot.png'))
    plt.close()

    # 7. Print markdown summary table
    print("| Feature Name | Pearson r with CS | Spearman r with CS |")
    print("|---|---|---|")
    import scipy.stats as stats
    for f in available_features:
        pearson_r, _ = stats.pearsonr(df_clean[f], df_clean['complexity_score'])
        spearman_r, _ = stats.spearmanr(df_clean[f], df_clean['complexity_score'])
        print(f"| {f} | {pearson_r:.4f} | {spearman_r:.4f} |")

if __name__ == '__main__':
    perform_eda()
