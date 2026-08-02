import json, yaml, pandas as pd
from dbs_policy import get_block_size_dbs, get_block_size_fixed_large, get_block_size_fixed_small
from qber_synth import generate_qber_series
from key_rate import compute_secure_key_rate
def run_simulation():
    with open("config.yaml", "r") as f: config = yaml.safe_load(f)
    rtt_series = pd.read_csv("data/rtt_time_series.csv")['rtt_ms'].tolist()
    qber_series = generate_qber_series(len(rtt_series), config)
    res = {'policies': ['dbs', 'fixed_large', 'fixed_small'], 'data': {p: {'block_sizes': [], 'skr': [], 't2k': [], 'failed_blocks': 0} for p in ['dbs', 'fixed_large', 'fixed_small']}, 'rtt_series': rtt_series, 'qber_series': qber_series.tolist()}
    for i in range(len(rtt_series)):
        rtt, qber = rtt_series[i], qber_series[i]
        policies = {'dbs': get_block_size_dbs(rtt, config), 'fixed_large': get_block_size_fixed_large(rtt, config), 'fixed_small': get_block_size_fixed_small(rtt, config)}
        for p_name, b_size in policies.items():
            skr = compute_secure_key_rate(b_size, qber, config['error_correction_efficiency_f'], float(config['epsilon_security']))
            t2k = config['t2k_c1'] * b_size + config['t2k_c2'] * rtt
            res['data'][p_name]['block_sizes'].append(b_size)
            res['data'][p_name]['skr'].append(skr)
            res['data'][p_name]['t2k'].append(t2k)
            if skr == 0.0: res['data'][p_name]['failed_blocks'] += 1
    with open("outputs/results.json", "w") as f: json.dump(res, f, indent=4)
if __name__ == "__main__": run_simulation()
