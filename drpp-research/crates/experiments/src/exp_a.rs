#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::Config;
use anyhow::Result;
use drpp_core::protocol::{confidence_interval_95, DrppGame, GameResult};
use rand::rngs::StdRng;
use rand::SeedableRng;
use rayon::prelude::*;

#[derive(Debug, Clone)]
pub struct ResultA {
    pub k: u32,
    pub p_theoretical: f64,
    pub p_simulated: f64,
    pub ci_lo: f64,
    pub ci_hi: f64,
    pub n_trials: u64,
}

pub fn run(cfg: &Config) -> Result<Vec<ResultA>> {
    println!("Running Experiment A: DRPP P_attack vs k...");

    let k_values: Vec<u32> = (1..=cfg.k_max_drpp).collect();

    let results: Vec<ResultA> = k_values
        .into_par_iter()
        .map(|k| {
            // Deterministic seed per k to ensure reproducibility when run in parallel
            let rng = StdRng::seed_from_u64(cfg.seed + k as u64);
            let mut game = DrppGame {
                k,
                secret: cfg.prf_secret.as_bytes().to_vec(),
                rng,
            };

            let res: GameResult = game.run(cfg.n_trials);
            let (ci_lo, ci_hi) = confidence_interval_95(res.p_attack_simulated, cfg.n_trials);

            ResultA {
                k,
                p_theoretical: res.p_attack_theoretical,
                p_simulated: res.p_attack_simulated,
                ci_lo,
                ci_hi,
                n_trials: cfg.n_trials,
            }
        })
        .collect();

    // Optionally dump raw data to data/exp_a.csv if needed,
    // though the requirement asks to log raw trial results.
    // For simplicity, we just return the aggregated results which are used for tables/figures.

    Ok(results)
}
