with open("scripts/04_statistical_evaluation.py", "r") as f:
    content = f.read()

# Replace the wilcoxon effect size calculation
import re
content = re.sub(
    r"stat, p_val = wilcoxon\(ensemble_f1s, baseline_f1s, zero_method='zsplit'\)\n    effect_size = stat / \(len\(ensemble_f1s\) \* \(len\(ensemble_f1s\) \+ 1\) / 2\)",
    "res = wilcoxon(ensemble_f1s, baseline_f1s, zero_method='zsplit', method='approx')\n    stat = res.statistic\n    p_val = res.pvalue\n    # Manual rank-biserial approximation\n    diffs = ensemble_f1s - baseline_f1s\n    diffs = diffs[diffs != 0]\n    ranks = np.argsort(np.argsort(np.abs(diffs))) + 1\n    pos_sum = np.sum(ranks[diffs > 0])\n    neg_sum = np.sum(ranks[diffs < 0])\n    total_rank_sum = len(diffs) * (len(diffs) + 1) / 2\n    effect_size = abs(pos_sum - neg_sum) / total_rank_sum if total_rank_sum > 0 else 0",
    content
)

with open("scripts/04_statistical_evaluation.py", "w") as f:
    f.write(content)
