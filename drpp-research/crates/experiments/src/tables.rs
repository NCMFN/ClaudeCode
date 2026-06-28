#![allow(clippy::too_many_arguments, clippy::unnecessary_cast)]
#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::exp_a::ResultA;
use crate::exp_b::ResultB;
use crate::exp_c::ResultC;
use crate::exp_d::ModalityResult;
use crate::exp_e::ResultE;
use crate::exp_f::ResultF;
use crate::exp_g::ResultG;
use crate::exp_i::ResultI;
use crate::Config;
use anyhow::Result;
use csv::Writer;
use drpp_core::stats::ConvergencePoint;
use std::fs::File;
use std::io::Write;

pub fn write_all(
    res_a: &[ResultA],
    res_b: &[ResultB],
    res_c: &[ResultC],
    res_d: &[ModalityResult],
    res_e: &[ResultE],
    res_f: &[ResultF],
    res_g: &[ResultG],
    _res_h: &[ConvergencePoint], // T19 and others may use this implicitly
    res_i: &[ResultI],
    cfg: &Config,
) -> Result<()> {
    println!("Generating tables...");

    write_t01_drpp_attack_probability(res_a)?;
    write_t02_collusion_attack_probability(res_b)?;
    write_t03_traditional_sensitivity(res_c)?;
    write_t04_modality_classifier_metrics(res_d)?;
    write_t05_confusion_matrix_values(res_d)?;
    write_t06_latency_statistics(res_e)?;
    write_t07_accuracy_vs_noise(res_d)?;
    write_t08_multimodal_attack_probability(res_f)?;
    write_t09_dos_simulation(res_g)?;
    write_t10_ablation_study(res_i)?;
    write_t11_simulation_config(cfg)?;
    write_t12_related_work_comparison()?;
    write_t13_modality_bit_capacity()?;
    write_t14_security_usability_matrix(res_a, res_e)?;
    write_t15_runtime_cost()?;
    write_t16_statistical_significance(res_a)?;
    write_t17_hardware_specification()?;
    write_t18_notation_glossary()?;
    write_t19_theoretical_vs_empirical_summary(res_a, res_b)?;
    write_t20_power_estimation()?;
    write_t21_side_channel_mitigation()?;

    Ok(())
}

fn write_table_formats(id: &str, name: &str, headers: &[&str], rows: &[Vec<String>]) -> Result<()> {
    // 1. CSV
    let csv_path = format!("tables/T{}_{}.csv", id, name);
    let mut wtr = Writer::from_path(&csv_path)?;
    wtr.write_record(headers)?;
    for row in rows {
        wtr.write_record(row)?;
    }
    wtr.flush()?;

    // 2. Markdown
    let md_path = format!("tables/T{}_{}.md", id, name);
    let mut f_md = File::create(&md_path)?;
    writeln!(f_md, "| {} |", headers.join(" | "))?;
    let sep: Vec<_> = headers.iter().map(|_| "---").collect();
    writeln!(f_md, "| {} |", sep.join(" | "))?;
    for row in rows {
        writeln!(f_md, "| {} |", row.join(" | "))?;
    }

    // 3. LaTeX
    let tex_path = format!("tables/T{}_{}.tex", id, name);
    let mut f_tex = File::create(&tex_path)?;
    let col_format = vec!["c"; headers.len()].join("|");
    writeln!(f_tex, "\\begin{{table}}[h]")?;
    writeln!(f_tex, "\\centering")?;
    writeln!(f_tex, "\\begin{{tabular}}{{|{}|}}", col_format)?;
    writeln!(f_tex, "\\hline")?;
    writeln!(f_tex, "{} \\\\ \\hline", headers.join(" & "))?;
    for row in rows {
        // Escape standard latex chars if needed
        let escaped_row: Vec<String> = row.iter().map(|s| s.replace('_', "\\_")).collect();
        writeln!(f_tex, "{} \\\\", escaped_row.join(" & "))?;
    }
    writeln!(f_tex, "\\hline")?;
    writeln!(f_tex, "\\end{{tabular}}")?;
    writeln!(f_tex, "\\caption{{{}}}", name.replace('_', " "))?;
    writeln!(f_tex, "\\label{{tab:T{}}}", id)?;
    writeln!(f_tex, "\\end{{table}}")?;

    Ok(())
}

fn write_t01_drpp_attack_probability(res: &[ResultA]) -> Result<()> {
    let headers = vec![
        "k",
        "p_theoretical",
        "p_simulated",
        "ci_lo",
        "ci_hi",
        "n_trials",
    ];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| {
            vec![
                r.k.to_string(),
                format!("{:.8e}", r.p_theoretical),
                format!("{:.8e}", r.p_simulated),
                format!("{:.8e}", r.ci_lo),
                format!("{:.8e}", r.ci_hi),
                r.n_trials.to_string(),
            ]
        })
        .collect();
    write_table_formats("01", "drpp_attack_probability", &headers, &rows)
}

fn write_t02_collusion_attack_probability(res: &[ResultB]) -> Result<()> {
    let headers = vec!["k", "n_colluders", "p_theoretical", "p_simulated"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| {
            vec![
                r.k.to_string(),
                r.n_colluders.to_string(),
                format!("{:.8e}", r.p_theoretical),
                format!("{:.8e}", r.p_simulated),
            ]
        })
        .collect();
    write_table_formats("02", "collusion_attack_probability", &headers, &rows)
}

fn write_t03_traditional_sensitivity(res: &[ResultC]) -> Result<()> {
    let headers = vec!["deception_prob", "p_simulated", "n_trials"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| {
            vec![
                format!("{:.2}", r.deception_prob),
                format!("{:.4}", r.p_simulated),
                r.n_trials.to_string(),
            ]
        })
        .collect();
    write_table_formats("03", "traditional_sensitivity", &headers, &rows)
}

fn write_t04_modality_classifier_metrics(res: &[ModalityResult]) -> Result<()> {
    let headers = vec![
        "modality",
        "classifier",
        "accuracy",
        "precision",
        "recall",
        "f1",
        "auc",
    ];
    let rows: Vec<Vec<String>> = res
        .iter()
        .filter(|r| r.noise_level == 0.0)
        .map(|r| {
            vec![
                r.modality.clone(),
                r.classifier.clone(),
                format!("{:.4}", r.metrics.accuracy),
                format!("{:.4}", r.metrics.precision),
                format!("{:.4}", r.metrics.recall),
                format!("{:.4}", r.metrics.f1),
                format!("{:.4}", r.metrics.auc),
            ]
        })
        .collect();
    write_table_formats("04", "modality_classifier_metrics", &headers, &rows)
}

fn write_t05_confusion_matrix_values(res: &[ModalityResult]) -> Result<()> {
    let headers = vec!["modality", "classifier", "TN", "FP", "FN", "TP"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .filter(|r| r.noise_level == 0.0)
        .map(|r| {
            vec![
                r.modality.clone(),
                r.classifier.clone(),
                r.cm.tn.to_string(),
                r.cm.fp.to_string(),
                r.cm.fn_val.to_string(),
                r.cm.tp.to_string(),
            ]
        })
        .collect();
    write_table_formats("05", "confusion_matrix_values", &headers, &rows)
}

fn write_t06_latency_statistics(res: &[ResultE]) -> Result<()> {
    let headers = vec!["modality", "mean_s", "median_s", "std_s", "p95_s"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| {
            vec![
                r.modality.clone(),
                format!("{:.3}", r.mean_s),
                format!("{:.3}", r.median_s),
                format!("{:.3}", r.std_s),
                format!("{:.3}", r.p95_s),
            ]
        })
        .collect();
    write_table_formats("06", "latency_statistics", &headers, &rows)
}

fn write_t07_accuracy_vs_noise(res: &[ModalityResult]) -> Result<()> {
    let headers = vec!["modality", "classifier", "noise_level", "accuracy"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| {
            vec![
                r.modality.clone(),
                r.classifier.clone(),
                format!("{:.3}", r.noise_level),
                format!("{:.4}", r.metrics.accuracy),
            ]
        })
        .collect();
    write_table_formats("07", "accuracy_vs_noise", &headers, &rows)
}

fn write_t08_multimodal_attack_probability(res: &[ResultF]) -> Result<()> {
    let headers = vec!["k", "single_modal", "dual_modal", "triple_modal"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| {
            vec![
                r.k.to_string(),
                format!("{:.8e}", r.single_modal),
                format!("{:.8e}", r.dual_modal),
                format!("{:.8e}", r.triple_modal),
            ]
        })
        .collect();
    write_table_formats("08", "multimodal_attack_probability", &headers, &rows)
}

fn write_t09_dos_simulation(res: &[ResultG]) -> Result<()> {
    let headers = vec!["time_s", "requests_no_rl", "requests_with_rl", "blocked"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| {
            vec![
                r.time_s.to_string(),
                r.requests_no_rl.to_string(),
                r.requests_with_rl.to_string(),
                r.blocked.to_string(),
            ]
        })
        .collect();
    write_table_formats("09", "dos_simulation", &headers, &rows)
}

fn write_t10_ablation_study(res: &[ResultI]) -> Result<()> {
    let headers = vec!["configuration", "p_attack"];
    let rows: Vec<Vec<String>> = res
        .iter()
        .map(|r| vec![r.configuration.clone(), format!("{:.6e}", r.p_attack)])
        .collect();
    write_table_formats("10", "ablation_study", &headers, &rows)
}

fn write_t11_simulation_config(cfg: &Config) -> Result<()> {
    let headers = vec!["parameter", "value"];
    let rows = vec![
        vec!["seed".to_string(), cfg.seed.to_string()],
        vec!["n_trials".to_string(), cfg.n_trials.to_string()],
        vec!["k_max_drpp".to_string(), cfg.k_max_drpp.to_string()],
        vec!["k_max_coll".to_string(), cfg.k_max_coll.to_string()],
        vec![
            "modality_samples".to_string(),
            cfg.modality_samples.to_string(),
        ],
    ];
    write_table_formats("11", "simulation_config", &headers, &rows)
}

// Stubs for static tables
fn write_t12_related_work_comparison() -> Result<()> {
    write_table_formats("12", "related_work_comparison", &["protocol"], &[])
}
fn write_t13_modality_bit_capacity() -> Result<()> {
    write_table_formats("13", "modality_bit_capacity", &["modality"], &[])
}
fn write_t14_security_usability_matrix(_res_a: &[ResultA], _res_e: &[ResultE]) -> Result<()> {
    write_table_formats("14", "security_usability_matrix", &["k"], &[])
}
fn write_t15_runtime_cost() -> Result<()> {
    write_table_formats("15", "runtime_cost", &["experiment"], &[])
}
fn write_t16_statistical_significance(_res_a: &[ResultA]) -> Result<()> {
    write_table_formats("16", "statistical_significance", &["k"], &[])
}
fn write_t17_hardware_specification() -> Result<()> {
    write_table_formats("17", "hardware_specification", &["component"], &[])
}
fn write_t18_notation_glossary() -> Result<()> {
    write_table_formats("18", "notation_glossary", &["symbol"], &[])
}
fn write_t19_theoretical_vs_empirical_summary(
    _res_a: &[ResultA],
    _res_b: &[ResultB],
) -> Result<()> {
    write_table_formats(
        "19",
        "theoretical_vs_empirical_summary",
        &["experiment"],
        &[],
    )
}
fn write_t20_power_estimation() -> Result<()> {
    write_table_formats("20", "power_estimation", &["modality"], &[])
}
fn write_t21_side_channel_mitigation() -> Result<()> {
    write_table_formats("21", "side_channel_mitigation", &["attack_type"], &[])
}
