#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::Config;
use anyhow::Result;
use rand::rngs::StdRng;
use rand::SeedableRng;
use rand_distr::{Distribution, Poisson};

#[derive(Debug, Clone)]
pub struct ResultG {
    pub time_s: u32,
    pub requests_no_rl: u32,
    pub requests_with_rl: u32,
    pub blocked: u32,
}

pub fn run(cfg: &Config) -> Result<Vec<ResultG>> {
    println!("Running Experiment G: DoS Simulation...");

    let duration_s = 60; // Simulate 1 minute of traffic
    let lambda = 5.0; // requests per second average
    let rate_limit = 2; // max requests processed per second

    let mut rng = StdRng::seed_from_u64(cfg.seed + 700);
    let dist = Poisson::new(lambda).unwrap();

    let mut results = Vec::with_capacity(duration_s as usize);

    let mut total_no_rl = 0;
    let mut total_with_rl = 0;
    let mut total_blocked = 0;

    for t in 1..=duration_s {
        let incoming = dist.sample(&mut rng) as u32;

        total_no_rl += incoming;

        let processed = incoming.min(rate_limit);
        let blocked = incoming - processed;

        total_with_rl += processed;
        total_blocked += blocked;

        results.push(ResultG {
            time_s: t,
            requests_no_rl: total_no_rl,
            requests_with_rl: total_with_rl,
            blocked: total_blocked,
        });
    }

    Ok(results)
}
