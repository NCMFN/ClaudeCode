#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::Config;
use anyhow::Result;
use drpp_core::protocol::DrppGame;
use rand::rngs::StdRng;
use rand::SeedableRng;
use rayon::prelude::*;

#[derive(Debug, Clone)]
pub struct ResultF {
    pub k: u32,
    pub single_modal: f64,
    pub dual_modal: f64,
    pub triple_modal: f64,
}

pub fn run(cfg: &Config) -> Result<Vec<ResultF>> {
    println!("Running Experiment F: Multi-modal Attack Probabilities...");

    // In multi-modal AND logic, to succeed, the adversary must guess
    // all components correctly. So P_attack = (P_single)^m
    // where P_single = 2^-k and m is number of modalities (1, 2, 3)

    let k_values: Vec<u32> = (1..=cfg.k_max_drpp).collect();

    let results: Vec<ResultF> = k_values
        .into_par_iter()
        .map(|k| {
            let rng = StdRng::seed_from_u64(cfg.seed + k as u64 * 3);
            let mut game = DrppGame {
                k,
                secret: cfg.prf_secret.as_bytes().to_vec(),
                rng,
            };

            let mut succ_1 = 0;
            let mut succ_2 = 0;
            let mut succ_3 = 0;

            for _ in 0..cfg.n_trials {
                // Simulated success is just independent Bernoulli trials
                let p1 = game.run(1).successes == 1;
                let p2 = game.run(1).successes == 1;
                let p3 = game.run(1).successes == 1;

                if p1 {
                    succ_1 += 1;
                }
                if p1 && p2 {
                    succ_2 += 1;
                }
                if p1 && p2 && p3 {
                    succ_3 += 1;
                }
            }

            ResultF {
                k,
                single_modal: succ_1 as f64 / cfg.n_trials as f64,
                dual_modal: succ_2 as f64 / cfg.n_trials as f64,
                triple_modal: succ_3 as f64 / cfg.n_trials as f64,
            }
        })
        .collect();

    Ok(results)
}
