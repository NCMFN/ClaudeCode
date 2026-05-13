import datetime
import os
import pandas as pd

def create_log():
    os.makedirs("results/logs", exist_ok=True)
    with open("results/logs/run_log.txt", "w") as f:
        f.write(f"Run started at: {datetime.datetime.now()}\n")
        f.write("Parameters: seed=42, models=[IF, OCSVM, AE, LSTM-AE, CNN-BiLSTM]\n")

        try:
            results = pd.read_csv("results/metrics/all_results.csv")
            f.write("Summary Results:\n")
            f.write(results.groupby("Model")["F1"].mean().to_string())
            f.write("\n")
        except:
            f.write("Results not available.\n")

        f.write(f"Run ended at: {datetime.datetime.now()}\n")

if __name__ == "__main__":
    create_log()
