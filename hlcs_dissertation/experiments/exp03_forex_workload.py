import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from core import hybrid_commitment
import config

plt.rcParams.update({'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11, 'xtick.labelsize': 10, 'ytick.labelsize': 10, 'figure.dpi': 300, 'savefig.dpi': 300})
sns.set_theme(style="whitegrid")

def generate_gbm(n_steps, s0, mu, sigma, dt, seed=42):
    rng = np.random.default_rng(seed)
    W = rng.standard_normal(n_steps)
    W = np.cumsum(W)*np.sqrt(dt)
    t = np.linspace(dt, n_steps*dt, n_steps)
    S = s0 * np.exp((mu - 0.5*sigma**2)*t + sigma*W)
    return np.insert(S, 0, s0)

def run():
    print("Running Exp03: Simulated Forex Workload")
    rng = np.random.default_rng(config.SEED)

    n_traders = 50
    orders_per_trader = 10
    total_orders = n_traders * orders_per_trader

    amounts = rng.uniform(1000, 100000, total_orders)
    directions = rng.choice(['BUY', 'SELL'], total_orders)

    lam = 100
    inter_arrivals = rng.exponential(1/lam, total_orders)
    timestamps = np.cumsum(inter_arrivals)

    S0, mu, sigma, dt = 1.0950, 0.0, 0.008, 0.001
    prices = generate_gbm(total_orders, S0, mu, sigma, dt, config.SEED)[:total_orders]

    trader_ids = np.repeat(np.arange(n_traders), orders_per_trader)
    rng.shuffle(trader_ids)

    pp = hybrid_commitment.setup(config.N, config.Q, config.SIGMA, seed=config.SEED)

    latencies = []

    for i in range(total_orders):
        msg = f"{trader_ids[i]}|{amounts[i]:.2f}|{directions[i]}|{prices[i]:.5f}".encode()
        msg = msg.ljust(config.MSG_BYTES, b'\0')[:config.MSG_BYTES]

        t0 = time.perf_counter_ns()
        C_tuple, st, _ = hybrid_commitment.commit(pp, msg)
        v1 = hybrid_commitment.fast_verify_C1(pp, C_tuple[0], st[0], msg)
        v2 = hybrid_commitment.full_verify_C2(pp, C_tuple[1], st[0], st[1], msg)
        t1 = time.perf_counter_ns()

        if not (v1 and v2):
            print("Warning: verification failed")

        latencies.append((t1-t0)/1e6)

    df_orders = pd.DataFrame({
        'Trader_ID': trader_ids,
        'Order_ID': np.arange(total_orders),
        'Amount': amounts,
        'Direction': directions,
        'Timestamp': timestamps,
        'Price': prices,
        'Latency_ms': latencies
    })

    # Tables
    df_trader_summary = df_orders.groupby('Trader_ID')['Latency_ms'].agg(['mean', 'std', 'min', 'max']).reset_index()
    df_trader_summary.to_csv('../tables/TABLE_05_Trader_Latency_Summary.csv', index=False)
    df_orders.to_csv('../tables/TABLE_06_Per_Order_Log.csv', index=False)

    # Burst test (simulated via simple inverse latency as capacity)
    burst_rates = [10**3, 10**4, 10**5, 5*10**5]
    burst_results = []
    avg_latency_s = np.mean(latencies) / 1000
    for br in burst_rates:
        processed_in_1ms = min(br * 0.001, 0.001 / avg_latency_s)
        burst_results.append({'Burst_Rate': br, 'Processed_1ms': processed_in_1ms})
    pd.DataFrame(burst_results).to_csv('../tables/TABLE_07_Burst_Test.csv', index=False)

    # Figures
    palette = ["#1F4E79", "#2E86AB", "#A23B72", "#F18F01", "#C73E1D"]

    plt.figure(figsize=(10, 6))
    plt.plot(generate_gbm(1000, S0, mu, sigma, dt, config.SEED), color=palette[0])
    plt.title('Figure 6: EUR/USD Simulated Tick Price')
    plt.ylabel('Price')
    plt.xlabel('Tick')
    plt.savefig('../figures/fig06_eur_usd_tick_data.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig06_eur_usd_tick_data.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig06_eur_usd_tick_data.txt', 'w') as f:
        f.write("Figure 6: EUR/USD simulated tick price chart using Geometric Brownian Motion model.")

    plt.figure(figsize=(10, 6))
    plt.plot(df_orders['Order_ID'], df_orders['Latency_ms'], alpha=0.3, color=palette[1], label='Latency')
    plt.plot(df_orders['Order_ID'], df_orders['Latency_ms'].rolling(50).mean(), color=palette[0], label='Rolling Mean (w=50)')
    plt.axhline(0.2, color='red', linestyle='--', label='0.2ms Threshold')
    plt.xlabel('Order ID')
    plt.ylabel('Latency (ms)')
    plt.title('Figure 7: Latency per Order Over Time')
    plt.legend()
    plt.savefig('../figures/fig07_latency_per_order_over_time.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig07_latency_per_order_over_time.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig07_latency_per_order_over_time.txt', 'w') as f:
        f.write("Figure 7: Latency per order over time with rolling mean (window=50) and 0.2ms threshold line.")

    plt.figure(figsize=(10, 6))
    sorted_traders = df_trader_summary.sort_values('mean')
    sns.barplot(x=np.arange(n_traders), y=sorted_traders['mean'], color=palette[2])
    plt.xlabel('Trader Rank')
    plt.ylabel('Mean Latency (ms)')
    plt.title('Figure 8: Per-Trader Average Latency')
    plt.savefig('../figures/fig08_per_trader_latency.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig08_per_trader_latency.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig08_per_trader_latency.txt', 'w') as f:
        f.write("Figure 8: Per-trader average latency bar chart, sorted from lowest to highest mean latency.")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_orders, x='Amount', y='Latency_ms', alpha=0.5, color=palette[3])
    plt.xlabel('Order Amount ($)')
    plt.ylabel('Commit Latency (ms)')
    plt.title('Figure 9: Amount vs Latency')
    plt.savefig('../figures/fig09_amount_vs_latency_scatter.png', bbox_inches='tight', pad_inches=0.1)
    plt.savefig('../figures/fig09_amount_vs_latency_scatter.pdf', bbox_inches='tight', pad_inches=0.1)
    plt.close()

    with open('../figures/fig09_amount_vs_latency_scatter.txt', 'w') as f:
        f.write("Figure 9: Scatter plot of order amount ($) vs. commit latency (ms).")

    print("Exp03 completed.")
    return 3, 4
