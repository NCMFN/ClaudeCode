#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::Config;
use anyhow::Result;
use drpp_core::adversary::collusion_guesses;
use drpp_core::protocol::DrppGame;
use rand::rngs::StdRng;
use rand::SeedableRng;
use rayon::prelude::*;

#[derive(Debug, Clone)]
pub struct ResultB {
    pub k: u32,
    pub n_colluders: usize,
    pub p_theoretical: f64,
    pub p_simulated: f64,
}

pub fn run(cfg: &Config) -> Result<Vec<ResultB>> {
    println!("Running Experiment B: Collusion Attack vs k...");

    // Create parameter combinations (k, n_colluders)
    let mut params = Vec::new();
    for &n in &cfg.colluders {
        for k in 1..=cfg.k_max_coll {
            params.push((k, n));
        }
    }

    let results: Vec<ResultB> = params
        .into_par_iter()
        .map(|(k, n)| {
            let mut rng = StdRng::seed_from_u64(cfg.seed + k as u64 + n as u64 * 100);
            let game = DrppGame {
                k,
                secret: cfg.prf_secret.as_bytes().to_vec(),
                rng: rng.clone(),
            };

            // Custom loop for collusion since DrppGame standard run is single guess
            let mut successes = 0;
            for _ in 0..cfg.n_trials {
                let guesses = collusion_guesses(k, n, &mut rng);
                // Verify if any guess is correct
                let challenge = drpp_core::protocol::generate_challenge(k, &mut rng);

                let mut trial_success = false;
                for guess in guesses {
                    if drpp_core::protocol::verify(&challenge, guess, &game.secret, k) {
                        trial_success = true;
                        break;
                    }
                }
                if trial_success {
                    successes += 1;
                }
            }

            let p_simulated = successes as f64 / cfg.n_trials as f64;
            let p_single = 2.0f64.powi(-(k as i32));
            // Theoretical prob = 1 - (1 - p_single)^n (assuming independent guesses)
            let p_theoretical = 1.0 - (1.0 - p_single).powi(n as i32);

            ResultB {
                k,
                n_colluders: n,
                p_theoretical,
                p_simulated,
            }
        })
        .collect();

    Ok(results)
}
