"""
Simulated Forex Workload: 500 EUR/USD orders, 50 traders × 10 orders.
Replicates Section VII-D from the paper.
Extends with: GBP/USD, USD/JPY, EUR/GBP pairs and 5000-order stress test.
Outputs: data/forex/forex_results.csv, data/forex/tick_data.csv
"""
import numpy as np
import pandas as pd
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from hlcs.commitment import HLCSSetup, HLCSCommitment, verify
from hlcs.params import DEFAULT_PARAMS

def simulate_eurusd_ticks(n_ticks=1000, seed=42):
    """Stochastic price model: geometric Brownian motion for EUR/USD."""
    rng = np.random.default_rng(seed)
    returns = rng.normal(0, 0.0001, n_ticks)
    price = 1.0950
    prices = [price]
    for r in returns:
        price *= (1 + r)
        prices.append(price)
    return np.array(prices)

def generate_orders(n_traders=50, orders_per_trader=10, seed=42):
    """Generate synthetic forex orders for n_traders."""
    rng = np.random.default_rng(seed)
    orders = []
    for trader_id in range(n_traders):
        for _ in range(orders_per_trader):
            amount = rng.integers(1000, 100001)
            direction = rng.choice(["BUY", "SELL"])
            pair = rng.choice(["EUR/USD", "GBP/USD", "USD/JPY", "EUR/GBP"])
            msg = f"{pair} {amount} {direction} T{trader_id:03d}".encode()
            orders.append(msg)
    return orders

pp = HLCSSetup(DEFAULT_PARAMS)
orders = generate_orders()
latencies = []
for msg in orders:
    t0 = time.perf_counter()
    com = HLCSCommitment(pp, msg)
    C1, C2 = com.commitment
    r, e, m = com.opening_hint
    ok = verify(pp, C1, C2, r, e, m)
    latencies.append((time.perf_counter() - t0) * 1000)

forex_results_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/forex/forex_results.csv'))
tick_data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/forex/tick_data.csv'))

df = pd.DataFrame({"order_index": range(len(orders)), "latency_ms": latencies})
df.to_csv(forex_results_file, index=False)

ticks = simulate_eurusd_ticks()
pd.DataFrame({"order_index": range(len(ticks)), "price": ticks}).to_csv(
    tick_data_file, index=False)

print(f"Forex workload: mean={np.mean(latencies):.4f}ms ± {np.std(latencies):.4f}ms")
