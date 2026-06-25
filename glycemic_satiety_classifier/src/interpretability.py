import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.tree import plot_tree
import shap
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def run_interpretability(out_dir, base_dir):
    fig_dir = os.path.join(out_dir, 'figures')
    tab_dir = os.path.join(out_dir, 'tables')

    X_train = pd.read_csv(os.path.join(out_dir, 'X_train.csv'))
    y_train = pd.read_csv(os.path.join(out_dir, 'y_train.csv'))['Satiety_Tier']
    X_test = pd.read_csv(os.path.join(out_dir, 'X_test.csv'))

    dt_model = joblib.load(os.path.join(out_dir, 'dt_best_model.pkl'))
    lr_model = joblib.load(os.path.join(out_dir, 'lr_best_model.pkl'))
    rf_model = joblib.load(os.path.join(out_dir, 'rf_best_model.pkl'))

    classes = ['LOW', 'MEDIUM', 'HIGH']

    tree = dt_model.named_steps['dt']
    fig, ax = plt.subplots(figsize=(20, 10))
    plot_tree(tree, feature_names=X_train.columns.tolist(), class_names=list(tree.classes_),
              filled=True, rounded=True, ax=ax, max_depth=5)
    plt.savefig(os.path.join(fig_dir, 'fig8_decision_tree.png'), dpi=200)
    plt.close()

    lr = lr_model.named_steps['lr']
    scaler = lr_model.named_steps['scaler']
    coefs = lr.coef_
    odds_ratios = np.exp(coefs)

    lr_res = []
    for i, class_name in enumerate(lr.classes_):
        for j, feature in enumerate(X_train.columns):
            lr_res.append({
                'Class': class_name,
                'Feature': feature,
                'Coefficient': coefs[i, j],
                'Odds_Ratio': odds_ratios[i, j]
            })
    lr_df = pd.DataFrame(lr_res)
    lr_df.to_csv(os.path.join(tab_dir, 'table3_lr_coefficients.csv'), index=False)

    fig, ax = plt.subplots(figsize=(12, 6))
    top_features = lr_df.groupby('Feature')['Odds_Ratio'].mean().sort_values(ascending=False).head(10).index
    plot_df = lr_df[lr_df['Feature'].isin(top_features)]
    sns.barplot(data=plot_df, x='Feature', y='Odds_Ratio', hue='Class', ax=ax)
    ax.axhline(1, color='r', linestyle='--')
    ax.set_title('Logistic Regression Odds Ratios (Top 10 Features by Mean)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'fig9_lr_odds_ratios.png'))
    plt.close()

    rf = rf_model.named_steps['rf']
    explainer = shap.TreeExplainer(rf)
    shap_values = explainer.shap_values(X_test)

    if isinstance(shap_values, list):
        mean_abs_shap = np.mean([np.abs(sv).mean(0) for sv in shap_values], axis=0)
        shap_values_plot = shap_values[1]
    else:
        mean_abs_shap = np.abs(shap_values).mean(axis=(0, 2))
        shap_values_plot = shap_values[:, :, 1]

    fig, ax = plt.subplots()
    shap.summary_plot(shap_values_plot, X_test, show=False)
    plt.savefig(os.path.join(fig_dir, 'fig10_shap_summary.png'))
    plt.close()

    fig, ax = plt.subplots()
    shap.summary_plot(shap_values_plot, X_test, plot_type="bar", show=False)
    plt.savefig(os.path.join(fig_dir, 'fig11_shap_bar.png'))
    plt.close()

    top_idx = np.argsort(mean_abs_shap)[::-1][:3]
    top_feats = [X_test.columns[i] for i in top_idx]

    if len(top_feats) > 0:
        fig, ax = plt.subplots()
        try:
            shap.dependence_plot(top_feats[0], shap_values_plot, X_test, show=False)
            plt.savefig(os.path.join(fig_dir, 'fig12_shap_dependence.png'))
        except:
            pass
        plt.close()

    shap_df = pd.DataFrame({'Feature': X_test.columns, 'Mean_Abs_SHAP': mean_abs_shap})
    shap_df = shap_df.sort_values('Mean_Abs_SHAP', ascending=False)
    shap_df.to_csv(os.path.join(tab_dir, 'table4_shap_values.csv'), index=False)

    df = pd.read_csv(os.path.join(base_dir, 'data', 'processed', 'satiety_features_engineered.csv'))

    pearson_gl, p_gl_p = pearsonr(df['GL'], df['Satiety_Index'])
    pearson_bulk, p_bulk_p = pearsonr(df['Water_Energy_Ratio'], df['Satiety_Index'])

    spearman_gl, p_gl_s = spearmanr(df['GL'], df['Satiety_Index'])
    spearman_bulk, p_bulk_s = spearmanr(df['Water_Energy_Ratio'], df['Satiety_Index'])

    hypo_res = pd.DataFrame([{
        'Metric': 'Pearson',
        'GL_Correlation': pearson_gl,
        'GL_P_Value': p_gl_p,
        'Bulk_Correlation': pearson_bulk,
        'Bulk_P_Value': p_bulk_p,
        'Is_Bulk_Stronger': abs(pearson_bulk) > abs(pearson_gl)
    }, {
        'Metric': 'Spearman',
        'GL_Correlation': spearman_gl,
        'GL_P_Value': p_gl_s,
        'Bulk_Correlation': spearman_bulk,
        'Bulk_P_Value': p_bulk_s,
        'Is_Bulk_Stronger': abs(spearman_bulk) > abs(spearman_gl)
    }])

    hypo_res.to_csv(os.path.join(tab_dir, 'table5_hypothesis_test.csv'), index=False)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'outputs')
    run_interpretability(out_dir, base_dir)

if __name__ == "__main__":
    main()
