import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

sns.set_theme(style="whitegrid")

def plot_model_performance(eval_results, output_path='figures/model_performance_benchmark.png'):
    """
    Plots a grouped bar chart comparing accuracy and macro-F1 across models.
    """
    models = list(eval_results.keys())
    accuracies = [res['accuracy'] for res in eval_results.values()]
    f1_scores = [res['f1_macro'] for res in eval_results.values()]

    x = np.arange(len(models))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, accuracies, width, label='Accuracy')
    rects2 = ax.bar(x + width/2, f1_scores, width, label='Macro-F1')

    ax.set_ylabel('Scores')
    ax.set_title('Model Performance Benchmark')
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.legend(loc='lower right')

    # Add values on bars
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_fault_probability_vs_length(model, X_test, preprocessor, label_encoder, output_path='figures/fault_probability_vs_length.png'):
    """
    Plots predicted probability of 'Insulation Degradation' vs 'length_nmi'.
    """
    # Create a synthetic range of length values while keeping others at their median
    df_synth = pd.DataFrame(columns=X_test.columns)

    lengths = np.linspace(X_test['length_nmi'].min(), X_test['length_nmi'].max(), 100)

    for col in df_synth.columns:
        if col == 'length_nmi':
            df_synth[col] = lengths
        else:
            df_synth[col] = X_test[col].median()

    # Need to add RC_interaction if it exists in preprocessor
    # Handled by features.py prepare_data before we get here typically, but let's assume X_test is already engineered.

    probs = model.predict_proba(df_synth)

    # Find index for 'Insulation Degradation'
    classes = list(label_encoder.classes_)
    target_idx = classes.index('Insulation Degradation') if 'Insulation Degradation' in classes else 0

    prob_target = probs[:, target_idx]

    plt.figure(figsize=(10, 6))
    plt.plot(lengths, prob_target, linewidth=2, color='darkred')
    plt.title("Predicted Probability of Insulation Degradation vs. Cable Length")
    plt.xlabel("Cable Length (nmi)")
    plt.ylabel("Probability")
    plt.figtext(0.5, -0.05,
                "Reference: Failure probability scaling follows implications of Kelvin's Law of Squares ($t \propto R\cdot C \cdot L^2$).",
                ha="center", fontsize=10, style='italic')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

def plot_historical_defect_breakdown(df, output_path='figures/historical_defect_breakdown.png'):
    """
    Plots a pie chart of class distribution.
    """
    counts = df['fault_class'].value_counts()

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    plt.title("Historical Defect Class Breakdown")
    plt.savefig(output_path, dpi=300)
    plt.close()
