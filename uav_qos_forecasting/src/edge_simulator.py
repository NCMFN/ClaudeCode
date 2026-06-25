import pandas as pd
import numpy as np
import os
import joblib
import time
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def run_simulation():
    results_df = pd.read_csv("outputs/tables/model_training_summary.csv")
    best_model_name = results_df.sort_values(by='F1_Weighted', ascending=False).iloc[0]['Model']
    model_path = f"outputs/models/{best_model_name}_best.pkl"
    model = joblib.load(model_path)
    X_test = pd.read_csv("data/synthetic/X_test.csv")
    y_test = pd.read_csv("data/synthetic/y_test.csv")['Performance_Class']

    idx = np.random.choice(len(X_test), size=1000, replace=(len(X_test)<1000))
    X_bench = X_test.iloc[idx]

    latencies = []
    _ = model.predict(X_bench.iloc[[0]])
    for i in range(len(X_bench)):
        start_t = time.perf_counter()
        _ = model.predict(X_bench.iloc[[i]])
        latencies.append((time.perf_counter() - start_t) * 1000)

    p99_lat = np.percentile(latencies, 99)
    if p99_lat >= 10:
        X_train = pd.read_csv("data/synthetic/X_train_resampled.csv")
        y_train = pd.read_csv("data/synthetic/y_train_resampled.csv")['Performance_Class']
        edge_model = DecisionTreeClassifier(max_depth=8, random_state=42)
        edge_model.fit(X_train, y_train)
        joblib.dump(edge_model, "outputs/models/EdgeFallback_best.pkl")
        model = edge_model

    active_model_path = "outputs/models/EdgeFallback_best.pkl" if 'edge_model' in locals() else model_path
    compressed_path = active_model_path.replace(".pkl", "_compressed.pkl")
    joblib.dump(model, compressed_path, compress=3)

    y_pred = model.predict(X_test)
    c2_log = pd.DataFrame({'True_Class': y_test, 'Predicted_Class': y_pred})

    alert_map = {0: '🔴 RED ALERT: Switch to autonomous failsafe', 1: '🟡 AMBER: Reduce payload data rate', 2: '🟢 GREEN: All systems nominal'}
    color_map = {0: 'red', 1: 'orange', 2: 'green'}
    c2_log['Alert_Message'] = c2_log['Predicted_Class'].map(alert_map)
    c2_log['Alert_Color'] = c2_log['Predicted_Class'].map(color_map)
    c2_log.to_csv("outputs/tables/c2_alert_log.csv", index=False)

    plt.figure(figsize=(12, 4))
    plt.scatter(c2_log.index, c2_log['Predicted_Class'], c=c2_log['Alert_Color'], s=20)
    plt.plot(c2_log.index, c2_log['Predicted_Class'], color='gray', alpha=0.3, linewidth=1)
    plt.yticks([0, 1, 2], ['Poor (0)', 'Moderate (1)', 'Optimal (2)'])
    plt.title('Figure 24: C2 Alert Timeline over Test Set')
    plt.xlabel('Time (Test Sample Index)')
    plt.ylabel('Predicted Network State')
    plt.tight_layout()
    plt.savefig('outputs/figures/fig_24_alert_timeline.png')
    plt.close()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_simulation()
