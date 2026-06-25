import pandas as pd
import numpy as np
import os
import joblib
import time
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, precision_recall_curve
from sklearn.preprocessing import label_binarize

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def run_evaluation():
    X_test = pd.read_csv("data/synthetic/X_test.csv")
    y_test = pd.read_csv("data/synthetic/y_test.csv")['Performance_Class']
    results_df = pd.read_csv("outputs/tables/model_training_summary.csv")

    with open('outputs/tables/cv_scores.json', 'r') as f: cv_scores_dict = json.load(f)

    models = ['LogisticRegression', 'RandomForest', 'GradientBoosting', 'XGBoost', 'LightGBM', 'MLP']
    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/tables", exist_ok=True)

    y_probs_dict = {}
    inference_times = {}

    for model_name in models:
        model_path = f"outputs/models/{model_name}_best.pkl"
        if not os.path.exists(model_path): continue

        model = joblib.load(model_path)
        idx = np.random.choice(len(X_test), size=1000, replace=(len(X_test)<1000))
        X_bench = X_test.iloc[idx]
        _ = model.predict(X_bench.iloc[[0]])

        start_t = time.perf_counter()
        for i in range(len(X_bench)): _ = model.predict(X_bench.iloc[[i]])
        end_t = time.perf_counter()

        avg_lat = ((end_t - start_t) / 1000) * 1000
        inference_times[model_name] = avg_lat

        y_pred = model.predict(X_test)
        try: y_probs_dict[model_name] = model.predict_proba(X_test)
        except: pass

        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        pd.DataFrame(report).transpose().to_csv(f"outputs/tables/classification_report_{model_name}.csv")

        cm = confusion_matrix(y_test, y_pred)
        cm_norm = cm.astype('float') / cm.sum(axis=1, keepdims=True)

        plt.figure(figsize=(6, 5))
        sns.heatmap(cm_norm, annot=True, fmt=".2%", cmap="Blues", xticklabels=['Poor', 'Moderate', 'Optimal'], yticklabels=['Poor', 'Moderate', 'Optimal'])
        plt.title(f'{model_name} Normalized Confusion Matrix')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.tight_layout()
        idx_fig = models.index(model_name) + 10
        plt.savefig(f'outputs/figures/fig_{idx_fig}_cm_{model_name}.png')
        plt.close()

    results_df['Inference_Latency_ms'] = results_df['Model'].map(inference_times)
    results_df.to_csv("outputs/tables/master_results_table.csv", index=False)

    plt.figure(figsize=(10, 6))
    melted = results_df.melt(id_vars='Model', value_vars=['Accuracy', 'F1_Weighted', 'ROC_AUC_OvR'], var_name='Metric', value_name='Score')
    sns.barplot(data=melted, x='Model', y='Score', hue='Metric', palette='Set2')
    plt.title('Figure 16: Model Performance Comparison')
    plt.ylim(0, 1.1)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_16_model_comparison.png')
    plt.close()

    top_models = results_df.sort_values(by='F1_Weighted', ascending=False)['Model'].head(2).tolist()
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
    n_classes = y_test_bin.shape[1]

    plt.figure(figsize=(8, 6))
    colors = ['blue', 'orange', 'green']
    linestyles = ['-', '--']
    for m_idx, m_name in enumerate(top_models):
        if m_name in y_probs_dict:
            probs = y_probs_dict[m_name]
            for i in range(n_classes):
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], probs[:, i])
                plt.plot(fpr, tpr, color=colors[i], linestyle=linestyles[m_idx], label=f'{m_name} Class {i} (AUC = {auc(fpr, tpr):.3f})')
    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Figure 17: Multi-class ROC Curves (Top 2 Models)')
    plt.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_17_roc_curves.png')
    plt.close()

    plt.figure(figsize=(8, 6))
    for m_idx, m_name in enumerate(['XGBoost', 'LightGBM']):
        if m_name in y_probs_dict:
            probs = y_probs_dict[m_name]
            for i in range(n_classes):
                prec, rec, _ = precision_recall_curve(y_test_bin[:, i], probs[:, i])
                plt.plot(rec, prec, color=colors[i], linestyle=linestyles[m_idx], label=f'{m_name} Class {i}')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Figure 18: Precision-Recall Curves')
    plt.legend(loc="lower left", fontsize=8)
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_18_pr_curves.png')
    plt.close()

    plt.figure(figsize=(10, 6))
    cv_data = [{'Model': m_name, 'CV_Accuracy': score} for m_name, scores in cv_scores_dict.items() for score in scores]
    sns.boxplot(data=pd.DataFrame(cv_data), x='Model', y='CV_Accuracy', palette='Set3', hue='Model', legend=False)
    plt.title('Figure 19: 5-Fold Cross-Validation Accuracy')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_19_cv_boxplots.png')
    plt.close()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_evaluation()
