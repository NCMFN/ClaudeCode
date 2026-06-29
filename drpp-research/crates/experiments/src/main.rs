use anyhow::Result;
use serde::Deserialize;
use std::fs;
use std::io::Write;
use std::path::Path;

mod exp_a;
mod exp_b;
mod exp_c;
mod exp_d;
mod exp_e;
mod exp_f;
mod exp_g;
mod exp_h;
mod exp_i;
mod figures;
mod report;
mod tables;

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub seed: u64,
    pub n_trials: u64,
    pub k_max_drpp: u32,
    pub k_max_coll: u32,
    pub colluders: Vec<usize>,
    pub noise_levels: Vec<f64>,
    pub deception_probs: Vec<f64>,
    pub modality_samples: usize,
    pub latency_samples: usize,
    pub convergence_k: u32,
    pub convergence_trials: Vec<u64>,
    pub prf_secret: String,
    pub figure_width_px: u32,
    pub figure_height_px: u32,
}

fn load_config(path: &str) -> Result<Config> {
    let content = fs::read_to_string(path)?;
    let config: Config = toml::from_str(&content)?;
    Ok(config)
}

fn write_figures_index() -> Result<()> {
    let mut file = fs::File::create("drpp-research/output/figures/index.md")?;
    writeln!(file, "# DRPP Figures Index\n")?;

    let figure_info = vec![
        ("F01", "F01_drpp_attack_probability_vs_k.png", "DRPP Attack Probability vs k", "Theoretical 2^-k bound vs Monte Carlo simulated P_attack (10,000 trials per k, with 95% Wilson confidence interval shading), k = 1–20."),
        ("F02", "F02_collusion_attack_vs_k.png", "Collusion Attack vs k", "Attack probability vs k for various numbers of colluders."),
        ("F03", "F03_full_comparison.png", "Full Comparison", "Comparison of DRPP, Collusion (n=2), and Traditional baselines."),
        ("F04", "F04_3d_surface_attack_k_n.png", "Attack Probability Contour (k vs n)", "3D surface contour showing attack probability across k and n."),
        ("F05", "F05_heatmap_collusion_k_n.png", "Heatmap of Collusion Success", "Grid heatmap representing the success probability of collusion attacks."),
        ("F06", "F06_security_usability_tradeoff.png", "Security vs Usability Tradeoff", "Dual Y-axis chart showing P_attack vs estimated system latency."),
        ("F07", "F07_roc_knock.png", "ROC Curve: Knock", "Receiver Operating Characteristic for the Knock modality."),
        ("F08", "F08_roc_touch.png", "ROC Curve: Touch", "Receiver Operating Characteristic for the Touch modality."),
        ("F09", "F09_roc_gesture.png", "ROC Curve: Gesture", "Receiver Operating Characteristic for the Gesture modality."),
        ("F10", "F10_confusion_matrix_combined.png", "Combined Confusion Matrix", "2x2 heatmap of confusion matrix values across combined modalities."),
        ("F11", "F11_feature_histograms.png", "Feature Histograms", "Distribution of legitimate vs spoofed features per modality."),
        ("F12", "F12_latency_boxplot.png", "Latency Boxplot", "Box-and-whisker plot of authentication latencies per modality."),
        ("F13", "F13_det_curve.png", "DET Curve", "Detection Error Tradeoff (FAR vs FRR) across modalities."),
        ("F14", "F14_accuracy_vs_noise.png", "Accuracy vs Noise Level", "Accuracy degradation across different modalities and classifiers as noise increases."),
        ("F15", "F15_monte_carlo_convergence.png", "Monte Carlo Convergence", "Simulation convergence towards theoretical bound over increasing trial counts."),
        ("F16", "F16_multimodal_bar.png", "Multi-modal Attack Probability", "Grouped bar chart showing attack probabilities for single, dual, and triple modal configurations."),
        ("F17", "F17_dos_simulation.png", "DoS Simulation", "Cumulative requests over time under simulated DoS attack with and without rate limiting."),
        ("F18", "F18_ablation_study.png", "Ablation Study", "Impact on attack probability when removing different DRPP components."),
        ("F19", "F19_radar_comparison.png", "Radar Comparison", "Qualitative assessment comparison using a spider/radar chart."),
        ("F20", "F20_sequence_diagram.png", "Sequence Diagram", "Drawn sequence diagram showing DRPP authentication flow."),
        ("F21", "F21_architecture_diagram.png", "Architecture Diagram", "System architecture map and interactions."),
        ("F22", "F22_cdf_guesses.png", "CDF of Guesses", "Cumulative distribution function showing probability of success within N guesses for various k."),
    ];

    for (id, filename, title, caption) in figure_info {
        writeln!(file, "## {} — {}", id, title)?;
        writeln!(file, "![{}]({})", id, filename)?;
        writeln!(file, "{}\n", caption)?;
    }

    Ok(())
}

fn write_tables_index() -> Result<()> {
    let mut file = fs::File::create("drpp-research/output/tables/index.md")?;
    writeln!(file, "# DRPP Tables Index\n")?;

    let table_info = vec![
        ("T01", "drpp_attack_probability", "k, p_theoretical, p_simulated, ci_lo, ci_hi, n_trials"),
        ("T02", "collusion_attack_probability", "k, n_colluders, p_theoretical, p_simulated"),
        ("T03", "traditional_sensitivity", "deception_prob, p_simulated, n_trials"),
        ("T04", "modality_classifier_metrics", "modality, classifier, accuracy, precision, recall, f1, auc"),
        ("T05", "confusion_matrix_values", "modality, classifier, TN, FP, FN, TP"),
        ("T06", "latency_statistics", "modality, mean_s, median_s, std_s, p95_s"),
        ("T07", "accuracy_vs_noise", "modality, classifier, noise_level, accuracy"),
        ("T08", "multimodal_attack_probability", "k, single_modal, dual_modal, triple_modal"),
        ("T09", "dos_simulation", "time_s, requests_no_rl, requests_with_rl, blocked"),
        ("T10", "ablation_study", "configuration, p_attack"),
        ("T11", "simulation_config", "parameter, value"),
        ("T12", "related_work_comparison", "protocol, deception_model, physical_presence, collusion_resistance, human_centric, boundary_binding"),
        ("T13", "modality_bit_capacity", "modality, encoding_scheme, effective_k_range, sensor"),
        ("T14", "security_usability_matrix", "k, p_attack, latency_s, knock_ok, touch_ok, gesture_ok"),
        ("T15", "runtime_cost", "experiment, wall_clock_s, trials_per_sec"),
        ("T16", "statistical_significance", "k, p_simulated, ci_lo, ci_hi, std_error"),
        ("T17", "hardware_specification", "component, spec, cost_usd"),
        ("T18", "notation_glossary", "symbol, meaning"),
        ("T19", "theoretical_vs_empirical_summary", "experiment, theoretical, empirical"),
        ("T20", "power_estimation", "modality, k, active_power_mw, duration_s, energy_mj"),
        ("T21", "side_channel_mitigation", "attack_type, mitigation, p_attack_no_mit, p_attack_with_mit"),
    ];

    for (id, name, columns) in table_info {
        writeln!(file, "## {} — {}", id, name)?;
        writeln!(file, "- **Columns**: {}\n", columns)?;
    }

    Ok(())
}

fn print_download_manifest() -> Result<()> {
    println!("✅ Figures written to drpp-research/output/figures/");
    let figures_dir = Path::new("output/figures");
    if figures_dir.exists() {
        let mut entries: Vec<_> = fs::read_dir(figures_dir)?
            .filter_map(|e| e.ok())
            .filter(|e| e.path().extension().and_then(|s| s.to_str()) == Some("png"))
            .collect();

        entries.sort_by_key(|dir| dir.path());

        for entry in entries {
            let metadata = entry.metadata()?;
            let file_size_kb = metadata.len() / 1024;
            println!("   {:<42} {} KB", entry.file_name().to_string_lossy(), file_size_kb);
        }
    }
    Ok(())
}

fn main() -> Result<()> {
    let cfg = load_config("experiments/config.toml")?;

    fs::create_dir_all("drpp-research/output/figures")?;
    fs::create_dir_all("drpp-research/output/tables")?;
    fs::create_dir_all("drpp-research/output/data")?;
    fs::create_dir_all("drpp-research/output/report")?;

    let _res_a = exp_a::run(&cfg)?;
    let _res_b = exp_b::run(&cfg)?;
    let _res_c = exp_c::run(&cfg)?;
    let _res_d = exp_d::run(&cfg)?;
    let _res_e = exp_e::run(&cfg)?;
    let _res_f = exp_f::run(&cfg)?;
    let _res_g = exp_g::run(&cfg)?;
    let _res_h = exp_h::run(&cfg)?;
    let _res_i = exp_i::run(&cfg)?;

    figures::generate_all(
        &_res_a, &_res_b, &_res_c, &_res_d, &_res_e, &_res_f, &_res_g, &_res_h, &_res_i,
    )?;
    tables::write_all(
        &_res_a, &_res_b, &_res_c, &_res_d, &_res_e, &_res_f, &_res_g, &_res_h, &_res_i, &cfg,
    )?;
    report::write("drpp-research/output/report/results_report.md", &_res_a, &_res_b)?;

    write_figures_index()?;
    write_tables_index()?;
    print_download_manifest()?;

    println!("✅ Framework initialized.");
    Ok(())
}
