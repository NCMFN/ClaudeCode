use anyhow::Result;
use serde::Deserialize;
use std::fs;

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

fn main() -> Result<()> {
    let cfg = load_config("experiments/config.toml")?;

    fs::create_dir_all("figures")?;
    fs::create_dir_all("tables")?;
    fs::create_dir_all("data")?;
    fs::create_dir_all("report")?;

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
    report::write("report/results_report.md", &_res_a, &_res_b)?;

    println!("✅ Framework initialized.");
    Ok(())
}
