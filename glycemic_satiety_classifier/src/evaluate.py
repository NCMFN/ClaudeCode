import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import label_binarize
from sklearn.model_selection import cross_val_score, StratifiedKFold

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def evaluate_models(out_dir):
    fig_dir = os.path.join(out_dir, 'figures')
    tab_dir = os.path.join(out_dir, 'tables')

    # Load test data
    X_test = pd.read_csv(os.path.join(out_dir, 'X_test.csv'))
    y_test = pd.read_csv(os.path.join(out_dir, 'y_test.csv'))['Satiety_Tier']
    X_train = pd.read_csv(os.path.join(out_dir, 'X_train.csv'))
    y_train = pd.read_csv(os.path.join(out_dir, 'y_train.csv'))['Satiety_Tier']

    models = {
        'DT': joblib.load(os.path.join(out_dir, 'dt_best_model.pkl')),
        'LR': joblib.load(os.path.join(out_dir, 'lr_best_model.pkl')),
        'RF': joblib.load(os.path.join(out_dir, 'rf_best_model.pkl'))
    }

    classes = ['LOW', 'MEDIUM', 'HIGH']

    metrics = []
    cms = {}
    roc_data = {}
    cv_scores_dict = {}

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    y_test_bin = label_binarize(y_test, classes=classes)
    n_classes = y_test_bin.shape[1]

    for name, model in models.items():
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)

        acc = accuracy_score(y_test, y_pred)
        prec_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
        rec_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        try:
            roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr', average='macro')
        except ValueError:
            roc_auc = np.nan

        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring='accuracy')
        cv_mean = np.mean(cv_scores)
        cv_std = np.std(cv_scores)
        cv_scores_dict[name] = cv_scores

        metrics.append({
            'Model': name,
            'Accuracy': acc,
            'Precision_Macro': prec_macro,
            'Recall_Macro': rec_macro,
            'F1_Macro': f1_macro,
            'F1_Weighted': f1_weighted,
            'ROC_AUC': roc_auc,
            'CV_Mean': cv_mean,
            'CV_Std': cv_std
        })

        cm = confusion_matrix(y_test, y_pred, labels=classes)
        cms[name] = cm

        roc_data[name] = {'fpr': dict(), 'tpr': dict(), 'roc_auc': dict()}
        for i, c in enumerate(classes):
            try:
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
                roc_data[name]['fpr'][c] = fpr
                roc_data[name]['tpr'][c] = tpr
                roc_data[name]['roc_auc'][c] = roc_auc_score(y_test_bin[:, i], y_prob[:, i])
            except Exception:
                pass

    # Save metrics table
    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv(os.path.join(tab_dir, 'table2_model_comparison.csv'), index=False)

    # Plot confusion matrices
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, name in zip(axes, ['DT', 'LR', 'RF']):
        sns.heatmap(cms[name], annot=True, fmt='d', cmap='Blues', ax=ax, xticklabels=classes, yticklabels=classes)
        ax.set_title(f'{name} Confusion Matrix')
        ax.set_ylabel('True')
        ax.set_xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'fig5_confusion_matrices.png'))
    plt.close()

    # Plot ROC curves
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, name in zip(axes, ['DT', 'LR', 'RF']):
        for c in classes:
            if c in roc_data[name]['fpr']:
                ax.plot(roc_data[name]['fpr'][c], roc_data[name]['tpr'][c],
                        label=f'{c} (AUC = {roc_data[name]["roc_auc"][c]:.2f})')
        ax.plot([0, 1], [0, 1], 'k--')
        ax.set_title(f'{name} ROC Curves')
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'fig6_roc_curves.png'))
    plt.close()

    # Plot CV score distribution
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=pd.DataFrame(cv_scores_dict), ax=ax)
    ax.set_title('Cross-Validation Accuracy Distribution')
    ax.set_ylabel('Accuracy')
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, 'fig7_cv_scores.png'))
    plt.close()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'outputs')
    evaluate_models(out_dir)

if __name__ == "__main__":
    main()
