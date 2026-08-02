import json, numpy as np, scipy.stats as stats
def ci(d): a = np.array(d); m = np.mean(a); h = stats.sem(a) * stats.t.ppf(0.975, len(a)-1) if len(a)>1 else 0; return m, m-h, m+h
def analyze_results():
    with open("outputs/results.json", "r") as f: res = json.load(f)
    s_out = {}
    for p in res['policies']:
        sm, sl, sh = ci(res['data'][p]['skr']); tm, tl, th = ci(res['data'][p]['t2k'])
        av = ((len(res['data'][p]['skr']) - res['data'][p]['failed_blocks']) / len(res['data'][p]['skr'])) * 100.0
        s_out[p] = {'skr_mean': sm, 'skr_ci_low': sl, 'skr_ci_high': sh, 't2k_mean': tm, 't2k_ci_low': tl, 't2k_ci_high': th, 'availability_percent': av, 'failure_rate_percent': 100.0-av}
    dbs_s, lg_s, sm_s = np.array(res['data']['dbs']['skr']), np.array(res['data']['fixed_large']['skr']), np.array(res['data']['fixed_small']['skr'])
    sl, pl = stats.wilcoxon(dbs_s, lg_s, zero_method='zsplit'); dl = dbs_s - lg_s; el = np.mean(dl)/np.std(dl) if np.std(dl)>0 else 0
    ss, ps = stats.wilcoxon(dbs_s, sm_s, zero_method='zsplit'); ds = dbs_s - sm_s; es = np.mean(ds)/np.std(ds) if np.std(ds)>0 else 0
    res['stats'] = s_out; res['tests'] = {'dbs_vs_large': {'statistic': sl, 'p_value': pl, 'effect_size_cohens_d': el}, 'dbs_vs_small': {'statistic': ss, 'p_value': ps, 'effect_size_cohens_d': es}}
    with open("outputs/results.json", "w") as f: json.dump(res, f, indent=4)
if __name__ == "__main__": analyze_results()
