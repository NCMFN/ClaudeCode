import pandas as pd
import numpy as np
import tensorflow as tf
import logging
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, confusion_matrix
import networkx as nx

from pipeline_utils import load_and_preprocess_data, extract_rolling_features
from anomaly_scoring import detect_micro_anomalies, compute_risk_score
from classification_sim import train_and_evaluate_models, simulate_cloud_edge

# Apply matplotlib styling rules
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def setup_logging():
    os.makedirs('results/logs', exist_ok=True)
    logging.basicConfig(
        filename='results/logs/pipeline.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def generate_system_architecture():
    G = nx.DiGraph()

    nodes = {
        "Cloud": (1, 3),
        "Edge Compute": (1, 2),
        "IoT Sensors": (1, 1),

        "Feature Engineering": (2, 2.5),
        "Anomaly Detection": (2, 2),
        "Risk Scoring": (2, 1.5),

        "Predictive Classification": (3, 3),
        "Simulation / Analytics": (3, 1),
    }

    edges = [
        ("IoT Sensors", "Edge Compute"),
        ("Edge Compute", "Feature Engineering"),
        ("Feature Engineering", "Anomaly Detection"),
        ("Anomaly Detection", "Risk Scoring"),
        ("Risk Scoring", "Cloud"),
        ("Cloud", "Predictive Classification"),
        ("Risk Scoring", "Simulation / Analytics"),
        ("Predictive Classification", "Simulation / Analytics")
    ]

    for n, pos in nodes.items():
        G.add_node(n, pos=pos)

    G.add_edges_from(edges)

    plt.figure(figsize=(10, 6))

    pos = nx.get_node_attributes(G, 'pos')

    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue',
            font_size=10, font_weight='bold', edge_color='gray',
            arrows=True, arrowsize=20, node_shape='s')

    plt.title('System Architecture: Smart Manufacturing Predictive Maintenance')
    plt.tight_layout()
    plt.savefig('system_architecture.png', bbox_inches='tight', dpi=300)
    plt.close()

def plot_feature_distributions(df_features):
    plt.figure(figsize=(10, 5))
    sns.boxplot(x='machine_id', y='vib_mean', data=df_features.head(1000))
    plt.title('Sample Vibration Mean Distribution by Machine')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('feature_dist.png')
    plt.close()

def plot_roc_curves(results, y_true):
    plt.figure(figsize=(8, 6))
    for model_name, res in results.items():
        if 'Probs' in res:
            fpr, tpr, _ = roc_curve(y_true, res['Probs'])
            plt.plot(fpr, tpr, label=f"{model_name} (AUC = {res['ROC-AUC']:.4f})")
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig('roc_curves.png')
    plt.close()

def plot_confusion_matrices(results, y_true):
    for model_name, res in results.items():
        if 'Probs' in res:
            preds = (res['Probs'] >= 0.5).astype(int)
            cm = confusion_matrix(y_true, preds)
            plt.figure(figsize=(6, 5))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f'{model_name} Confusion Matrix')
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            plt.tight_layout()
            plt.savefig(f'cm_{model_name}.png')
            plt.close()

def plot_risk_distribution(df):
    plt.figure(figsize=(8, 5))
    sns.histplot(df['risk_score'], bins=50, kde=True)
    plt.axvline(x=75, color='r', linestyle='--', label='High Risk Threshold (75)')
    plt.title('Distribution of Proactive Downtime Risk Scores')
    plt.xlabel('Risk Score')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.savefig('risk_score_distribution.png')
    plt.close()

def plot_timeline(df, machine_id):
    df_m = df[df['machine_id'] == machine_id].copy()
    plt.figure(figsize=(15, 5))
    plt.plot(df_m['timestamp'], df_m['risk_score'], label='Risk Score')

    anoms = df_m[df_m['micro_anomaly'] == 1]
    plt.scatter(anoms['timestamp'], [0]*len(anoms), color='orange', marker='x', label='Micro Anomaly')

    fails = df_m[df_m['maintenance_required'] == 1]
    plt.scatter(fails['timestamp'], [100]*len(fails), color='red', marker='v', s=100, label='Maintenance Required')

    plt.axhline(y=75, color='r', linestyle='--', alpha=0.5)
    plt.title(f'Timeline for Machine {machine_id}')
    plt.xlabel('Time')
    plt.ylabel('Score / Event')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'timeline_{machine_id}.png')
    plt.close()

def main():
    setup_logging()
    logging.info("Starting Pipeline")

    np.random.seed(42)
    tf.random.set_seed(42)

    os.makedirs('outputs', exist_ok=True)
    os.makedirs('models', exist_ok=True)

    logging.info("Generating system architecture diagram...")
    generate_system_architecture()

    logging.info("Loading data...")
    df = load_and_preprocess_data('data/smart_manufacturing_data.csv')

    logging.info("Extracting rolling features...")
    df_features = extract_rolling_features(df, window_min=10)

    df_features.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_features.fillna(0, inplace=True)

    logging.info("Detecting micro-anomalies...")
    sensor_cols = ['vibration', 'pressure', 'energy_consumption', 'humidity', 'temperature']
    df_anom = detect_micro_anomalies(df_features, sensor_cols)

    logging.info("Computing risk scores with grid search params...")
    df_risk = compute_risk_score(df_anom, alpha=0.45, beta=0.30, gamma=0.25)
    df_risk.to_csv('outputs/risk_scores.csv', index=False)

    logging.info("Training and evaluating models...")
    drop_cols = ['timestamp', 'machine_id', 'maintenance_required', 'anomaly_flag', 'if_anomaly', 'lstm_anomaly']
    features = [c for c in df_risk.columns if c not in drop_cols]

    df_risk.replace([np.inf, -np.inf], 0, inplace=True)

    results = train_and_evaluate_models(df_risk, features, target='maintenance_required')

    logging.info("Simulating Cloud-Edge Architecture...")
    simulate_cloud_edge(df_risk)

    logging.info("Generating plots...")
    plot_feature_distributions(df_features)
    plot_roc_curves(results, df_risk['maintenance_required'].values)
    plot_confusion_matrices(results, df_risk['maintenance_required'].values)
    plot_risk_distribution(df_risk)

    sample_machine = df_risk['machine_id'].iloc[0]
    plot_timeline(df_risk, sample_machine)

    with open('outputs/classification_report.txt', 'w') as f:
        for m, res in results.items():
            f.write(f"Model: {m}\n")
            f.write(f"Precision: {res['Precision']:.4f}\n")
            f.write(f"Recall: {res['Recall']:.4f}\n")
            f.write(f"F1-Score: {res['F1-Score']:.4f}\n")
            f.write(f"ROC-AUC: {res['ROC-AUC']:.4f}\n")
            f.write(f"Lead Time (min): {res['Lead Time (min)']:.2f}\n")
            f.write("-" * 30 + "\n")

    logging.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
