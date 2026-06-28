import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from statsmodels.stats.outliers_influence import variance_inflation_factor

class MulticollinearityAnalyzer:
    def __init__(self):
        os.makedirs(config.FIGURE_DIR, exist_ok=True)
        os.makedirs(config.RESULTS_DIR, exist_ok=True)

    def compute_correlation_matrix(self, X):
        corr_matrix = X.corr(method='pearson')

        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        cmap = sns.diverging_palette(230, 20, as_cmap=True)

        sns.heatmap(corr_matrix, mask=mask, cmap=cmap, vmax=1.0, vmin=-1.0, center=0,
                    square=True, linewidths=.5, cbar_kws={"shrink": .5}, annot=True, fmt=".2f", annot_kws={"size": 8})

        plt.title('Feature Correlation Heatmap')
        plt.tight_layout()
        filepath = os.path.join(config.FIGURE_DIR, 'correlation_heatmap.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return corr_matrix

    def compute_vif(self, X):
        vif_data = []
        for i in range(X.shape[1]):
            try:
                vif = variance_inflation_factor(X.values, i)
            except Exception as e:
                vif = float('inf')
            vif_data.append({"Feature": X.columns[i], "VIF": vif})

        vif_df = pd.DataFrame(vif_data).sort_values(by="VIF", ascending=False).reset_index(drop=True)

        csv_filepath = os.path.join(config.RESULTS_DIR, 'vif_scores.csv')
        vif_df.to_csv(csv_filepath, index=False)

        plt.figure(figsize=(10, 8))
        colors = []
        for vif in vif_df["VIF"]:
            if vif > 10:
                colors.append('red')
            elif vif >= 5:
                colors.append('yellow')
            else:
                colors.append('green')

        sns.barplot(x="VIF", y="Feature", data=vif_df, hue="Feature", palette=colors, legend=False)
        plt.title('Variance Inflation Factor (VIF) Scores')
        plt.axvline(x=10, color='r', linestyle='--', alpha=0.5)
        plt.axvline(x=5, color='y', linestyle='--', alpha=0.5)
        plt.xscale('log')
        plt.tight_layout()

        fig_filepath = os.path.join(config.FIGURE_DIR, 'vif_scores.png')
        plt.savefig(fig_filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return vif_df

    def recommend_features(self, vif_df, corr_matrix):
        features_to_drop = set()

        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) > 0.95:
                    high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))

        for f1, f2, r in high_corr:
            if f1 in features_to_drop or f2 in features_to_drop:
                continue

            vif1 = vif_df[vif_df['Feature'] == f1]['VIF'].values[0]
            vif2 = vif_df[vif_df['Feature'] == f2]['VIF'].values[0]

            if vif1 > vif2:
                features_to_drop.add(f1)
            else:
                features_to_drop.add(f2)

        original_features = set(corr_matrix.columns)
        recommended_features = original_features - features_to_drop
        return list(recommended_features)
