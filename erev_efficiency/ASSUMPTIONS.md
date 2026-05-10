# Modeling Assumptions
1. **Fuel Consumption Proxy:** Direct fuel consumption is absent from standard EV datasets. We assume 8.8 kWh/L gasoline energy density operating at an average 30% ICE efficiency. Thus, Estimated Fuel (L) = Restored Energy (kWh) / (8.8 * 0.3).
2. **Generator Activation:** Defined as rows where `soc_pct` drops below a rolling 10-row minimum, followed by a positive spike in `charge_rate_kw`.
3. **Missing Features:** Since the datasets do not all strictly overlap, certain proxy or derived calculations (like using battery voltage/current to compute power demand) are applied.
4. **Leakage Prevention:** To avoid perfect algebraic target leakage, SoC rolling features and deltas are shifted by 1 row to represent the *past* SoC context rather than mathematically leaking the *current* target SoC.
