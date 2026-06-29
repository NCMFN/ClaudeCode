#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::Config;
use anyhow::Result;
use drpp_core::adversary::traditional_adversary;
use rand::rngs::StdRng;
use rand::SeedableRng;
use rayon::prelude::*;

#[derive(Debug, Clone)]
pub struct ResultC {
    pub deception_prob: f64,
    pub p_simulated: f64,
    pub n_trials: u64,
}

pub fn run(cfg: &Config) -> Result<Vec<ResultC>> {
    println!("Running Experiment C: Traditional Baseline Sensitivity...");

    let results: Vec<ResultC> = cfg
        .deception_probs
        .par_iter()
        .map(|&prob| {
            // Multiply prob by a large constant so it's a unique int for seeding
            let mut rng = StdRng::seed_from_u64(cfg.seed + (prob * 10000.0) as u64);

            let mut successes = 0;
            for _ in 0..cfg.n_trials {
                if traditional_adversary(prob, &mut rng) {
                    successes += 1;
                }
            }

            let p_simulated = successes as f64 / cfg.n_trials as f64;

            ResultC {
                deception_prob: prob,
                p_simulated,
                n_trials: cfg.n_trials,
            }
        })
        .collect();

    Ok(results)
}
