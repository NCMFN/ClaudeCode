import pandas as pd
import numpy as np

def run_experiment_loop(datasets_dict, preprocess_fn, train_fn, explainer_fns, metric_fns):
    """
    Orchestrates the main experimental loop across all datasets, methods, and seeds.
    Returns dictionaries of collected results.
    """
    seeds = [42, 52, 62, 72, 82]
    all_metrics_results = []

    # Unpack functions
    calculate_fidelity = metric_fns['fidelity']
    calculate_stability = metric_fns['stability']
    calculate_simplicity = metric_fns['simplicity']
    calculate_relevance = metric_fns['relevance']
    calculate_q_score = metric_fns['q_score']

    for dataset_name, df in datasets_dict.items():
        print(f"\n================ Running experiments for {dataset_name} ================")

        for seed in seeds:
            print(f"--- Seed: {seed} ---")

            # Note: We preprocess per seed because the train-test split depends on random_state
            data_dict = preprocess_fn(df.copy(), dataset_name, seed)
            X_train = data_dict['X_train']
            X_test = data_dict['X_test']
            X_train_unscaled = data_dict['X_train_unscaled']
            y_train = data_dict['y_train']
            y_test = data_dict['y_test']
            feature_names = data_dict['feature_names']

            # Train model
            model = train_fn(X_train, y_train, seed=seed)
            X_train_mean = np.mean(X_train, axis=0)

            # Initialize explainers
            shap_explainer = explainer_fns['shap'](model)
            lime_explainer = explainer_fns['lime'](X_train, feature_names)

            # Generate Base Explanations
            shap_vals = shap_explainer.explain(X_test)
            lime_vals = lime_explainer.explain(model, X_test, num_samples=100) # Reduce LIME perturbations for speed

            methods = [
                ('SHAP', shap_vals, lambda X: shap_explainer.explain(X)),
                ('LIME', lime_vals, lambda X: lime_explainer.explain(model, X, num_samples=100))
            ]

            for method_name, base_vals, exp_func in methods:
                # Calculate metrics
                fidelity = calculate_fidelity(model, X_test, X_train_mean, base_vals)
                stability = calculate_stability(model, X_test, exp_func, sigma=0.01)
                simplicity = calculate_simplicity(base_vals, method=method_name.lower())
                relevance, kappa = calculate_relevance(base_vals, feature_names, dataset_name)
                q_score = calculate_q_score(fidelity, stability, simplicity, relevance)

                result_row = {
                    'Dataset': dataset_name,
                    'Seed': seed,
                    'Method': method_name,
                    'Fidelity': fidelity,
                    'Stability_0.01': stability,
                    'Simplicity': simplicity,
                    'Relevance': relevance,
                    'Kappa': kappa,
                    'Q_Score': q_score
                }
                all_metrics_results.append(result_row)

    return pd.DataFrame(all_metrics_results)


from scipy import stats

def run_statistical_tests(results_df):
    """
    Runs paired t-tests (SHAP vs LIME) for all four metrics.
    Includes Shapiro-Wilk for normality, Holm-Bonferroni correction, and Cohen's d.
    """
    metrics = ['Fidelity', 'Stability_0.01', 'Simplicity', 'Relevance']
    test_results = []

    # We aggregate over datasets and seeds. Or we pair them exactly by Dataset+Seed.
    # Pairing by Dataset+Seed gives us 6 datasets * 5 seeds = 30 paired samples.

    # Let's align SHAP and LIME results
    shap_df = results_df[results_df['Method'] == 'SHAP'].set_index(['Dataset', 'Seed'])
    lime_df = results_df[results_df['Method'] == 'LIME'].set_index(['Dataset', 'Seed'])

    # Align indices to be safe
    common_idx = shap_df.index.intersection(lime_df.index)
    shap_df = shap_df.loc[common_idx]
    lime_df = lime_df.loc[common_idx]

    p_values_raw = []

    for metric in metrics:
        shap_vals = shap_df[metric].values
        lime_vals = lime_df[metric].values

        diff = shap_vals - lime_vals

        # Check Normality assumption (Shapiro-Wilk)
        # If difference is all zeros (e.g. relevance is same), shapiro fails or warns
        if np.std(diff) < 1e-8:
            w_stat, shapiro_p = np.nan, np.nan
            t_stat, p_val = np.nan, 1.0 # no difference
            cohens_d = 0.0
        else:
            w_stat, shapiro_p = stats.shapiro(diff)
            t_stat, p_val = stats.ttest_rel(shap_vals, lime_vals)

            # Cohen's d for paired samples: mean(diff) / std(diff)
            cohens_d = np.mean(diff) / np.std(diff, ddof=1)

        p_values_raw.append(p_val)

        # 95% CI for difference
        if np.std(diff) < 1e-8:
            ci_lower, ci_upper = 0.0, 0.0
        else:
            se = np.std(diff, ddof=1) / np.sqrt(len(diff))
            margin = stats.t.ppf(0.975, len(diff)-1) * se
            mean_diff = np.mean(diff)
            ci_lower = mean_diff - margin
            ci_upper = mean_diff + margin

        test_results.append({
            'Metric': metric,
            'SHAP_Mean': np.mean(shap_vals),
            'LIME_Mean': np.mean(lime_vals),
            'T_Stat': t_stat,
            'P_Value_Raw': p_val,
            'Shapiro_P': shapiro_p,
            'Cohens_D': cohens_d,
            'CI_Lower_95': ci_lower,
            'CI_Upper_95': ci_upper
        })

    # Holm-Bonferroni Correction
    # Sort indices by p-value (ascending)
    test_results_df = pd.DataFrame(test_results)

    # Handle NaNs in P_Value_Raw before sorting
    test_results_df['P_Value_Raw'] = test_results_df['P_Value_Raw'].fillna(1.0)

    sorted_indices = test_results_df['P_Value_Raw'].argsort()
    m = len(metrics)
    p_adj = np.zeros(m)

    for rank, idx in enumerate(sorted_indices):
        alpha_adj_factor = m - rank
        adj_p = min(1.0, test_results_df.loc[idx, 'P_Value_Raw'] * alpha_adj_factor)
        # Holm-Bonferroni enforces monotonicity
        if rank > 0:
            prev_idx = sorted_indices[rank - 1]
            adj_p = max(adj_p, p_adj[prev_idx])
        p_adj[idx] = adj_p

    test_results_df['P_Value_Adj_Holm'] = p_adj
    return test_results_df

def run_ablation_study(results_df):
    """
    Computes Q scores for the ablation study configurations.
    1. Full
    2. w/o Fidelity
    3. w/o Stability
    4. w/o Simplicity
    5. w/o Relevance
    """
    ablation_results = []

    # We do this per method
    for method in ['SHAP', 'LIME']:
        method_df = results_df[results_df['Method'] == method]

        mean_fid = method_df['Fidelity'].mean()
        mean_stab = method_df['Stability_0.01'].mean()
        mean_simp = method_df['Simplicity'].mean()
        mean_rel = method_df['Relevance'].mean()

        # 1. Full
        q_full = 0.25 * (mean_fid + mean_stab + mean_simp + mean_rel)

        # 2. w/o Fidelity (avg of remaining 3)
        q_no_fid = (1/3) * (mean_stab + mean_simp + mean_rel)

        # 3. w/o Stability
        q_no_stab = (1/3) * (mean_fid + mean_simp + mean_rel)

        # 4. w/o Simplicity
        q_no_simp = (1/3) * (mean_fid + mean_stab + mean_rel)

        # 5. w/o Relevance
        q_no_rel = (1/3) * (mean_fid + mean_stab + mean_simp)

        ablation_results.append({
            'Method': method,
            'Full_Q': q_full,
            'No_Fidelity_Q': q_no_fid,
            'No_Stability_Q': q_no_stab,
            'No_Simplicity_Q': q_no_simp,
            'No_Relevance_Q': q_no_rel
        })

    return pd.DataFrame(ablation_results)
