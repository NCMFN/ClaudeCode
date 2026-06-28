#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::Config;
use anyhow::Result;
use drpp_core::stats::{convergence_series, ConvergencePoint};

pub fn run(cfg: &Config) -> Result<Vec<ConvergencePoint>> {
    println!("Running Experiment H: Monte Carlo Convergence...");

    let results = convergence_series(
        cfg.convergence_k,
        cfg.prf_secret.as_bytes(),
        &cfg.convergence_trials,
        cfg.seed + 800,
    );

    Ok(results)
}
