import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})

def main():
    xgb_results = pd.read_csv("outputs/tables/xgb_results.csv")
    lstm_results = pd.read_csv("outputs/tables/lstm_results.csv")
    comparison = pd.concat([xgb_results, lstm_results], ignore_index=True)
    comparison.to_csv("outputs/tables/model_comparison.csv", index=False)

    df_raw = pd.read_parquet("data/processed/heliospredict_processed.parquet")
    df_raw['day_of_week'] = df_raw['time'].dt.dayofweek
    df_raw['hour'] = df_raw['time'].dt.hour
    heatmap_data = df_raw.pivot_table(index='day_of_week', columns='hour', values='lux', aggfunc='mean').fillna(0)

    plt.figure(figsize=(10, 4))
    sns.heatmap(heatmap_data, cmap='YlOrRd')
    plt.savefig("outputs/figures/diurnal_heatmap.png"); plt.close()

if __name__ == "__main__": main()
