1. **Setup Environment**: We've already created the required directory structure (`data_loaders/`, `model/`, `policy/`, `analysis/`, `tests/`) and added the `NetLatency-Data` repo as a submodule.
2. **Implement NetLatency Loader** (`data_loaders/netlatency_loader.py`):
   - Iterate through `SeattleData_*` files (1 to 688).
   - Read the matrix in each file. Extract a specific set of indices (or randomly sample, but let's take a single pair for a continuous time series or aggregate across a few pairs, or randomly sample one RTT from each matrix). Since we need a time series, taking a fixed (i, j) pair or the mean of the matrix for each time slice makes sense. The prompt says: "Write a loader that reshapes each time slice into a distribution of RTT samples (ms) and exposes it as a pandas Series indexed by synthetic timestamps at a configurable sampling interval." I'll read the files in order, and for each time slice, we can pick a specific RTT (e.g., node 0 to node 1), or sample from the distribution. Wait, "reshapes each time slice into a distribution of RTT samples... exposes it as a pandas Series indexed by synthetic timestamps". This suggests we might flatten the matrix and take a random sample for each timestamp, or create a Series where each timestamp corresponds to a single RTT value from the distribution of that time slice.
   - Wait, if it's 688 time slices, and we want a single pandas Series of RTTs: we can simulate taking one RTT measurement at each timestep by picking a random non-zero RTT from that slice's matrix, or we can just pick a fixed node pair `(i, j)`. The simplest is to pick a fixed random pair or just a single sample per slice to form a time series of length 688. I will randomly sample one RTT per slice, or take a specific pair. Let's provide a function that samples one RTT per time slice, returning a Pandas Series of length 688.
3. **Implement Fidelity Model** (`model/fidelity.py`):
   - Define a function `calculate_fidelity(rtt, t2)` implementing `F(t) = 0.5 + 0.5 * exp(-rtt / t2)`.
   - Define configs for T2: `IonQ Aria: 1.0`, `AQT ring chip: 0.05`.
4. **Implement Policies** (`policy/adaptive_ttl.py`, `policy/static_ttl.py`):
   - Adaptive TTL: takes current RTT and T2, calculates fidelity, if < 0.85 return FLUSH, else HOLD.
   - Static TTL: takes current time since buffer reset and a fixed timeout, if time > timeout return FLUSH, else HOLD. The prompt says "static-TTL baseline policy (fixed timeout, no telemetry awareness)".
5. **Implement Simulation Loop** (`simulate.py`):
   - Load RTT time series.
   - Loop over time series. Keep track of "time in buffer". Wait, the prompt says:
     "The policy must monitor real-time RTT, compute fidelity decay, and flush the buffer before that threshold is crossed."
     And "F(t) = 0.5 + 0.5 * exp(-t / T2), where t is the measured classical RTT latency for that time step".
     This means `t` in the formula is just the RTT! Not the time since buffer was created. So fidelity depends only on the current network RTT.
     Wait, "Monitor: pull next RTT sample... Calculate: compute F(t)... Compare: check F(t) against 0.85... Act: log FLUSH or HOLD".
     So the "buffer" resets. A FLUSH means we flushed it.
   - Run both policies over the dataset.
   - Export CSV.
   - Export JSON matching Open MCT schema: `{"timestamp": ..., "value": ..., "id": ...}`.
6. **Analysis and Plotting** (`analysis/report.py`):
   - Read simulation CSV.
   - Plot Fidelity decay curve as a function of RTT with the 0.85 threshold.
   - Plot comparison of policies (Zombie keys vs unnecessary flushes).
7. **Write Tests** (`tests/test_model.py`, `tests/test_policies.py`):
   - pytest for fidelity calculation, TTL logic.
8. **Write README.md**:
   - Explain the model, limitations, and how to run.
