#![allow(dead_code)]
use crate::Config;
use anyhow::Result;
use rand::rngs::StdRng;
use rand::SeedableRng;
use rand_distr::{Distribution, LogNormal};

#[derive(Debug, Clone)]
pub struct ResultE {
    pub modality: String,
    pub mean_s: f64,
    pub median_s: f64,
    pub std_s: f64,
    pub p95_s: f64,
    pub latencies: Vec<f64>,
}

pub fn run(cfg: &Config) -> Result<Vec<ResultE>> {
    println!("Running Experiment E: Latency Simulation...");

    let modalities = vec![
        ("knock", 0.5, 0.4), // LogNormal mu, sigma
        ("touch", 1.2, 0.3),
        ("gesture", 2.0, 0.5),
    ];

    let mut results = Vec::new();
    let mut rng = StdRng::seed_from_u64(cfg.seed + 500);

    for (mod_name, mu, sigma) in modalities {
        let dist = LogNormal::new(mu, sigma).unwrap();
        let mut latencies = Vec::with_capacity(cfg.latency_samples);
        let mut sum = 0.0;

        for _ in 0..cfg.latency_samples {
            let val = dist.sample(&mut rng);
            latencies.push(val);
            sum += val;
        }

        let mean_s = sum / cfg.latency_samples as f64;

        let mut sum_sq_diff = 0.0;
        for &val in &latencies {
            sum_sq_diff += (val - mean_s).powi(2);
        }
        let std_s = (sum_sq_diff / cfg.latency_samples as f64).sqrt();

        let mut sorted = latencies.clone();
        sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());

        let median_s = sorted[cfg.latency_samples / 2];
        let p95_idx = (cfg.latency_samples as f64 * 0.95) as usize;
        let p95_s = sorted[p95_idx.min(cfg.latency_samples - 1)];

        results.push(ResultE {
            modality: mod_name.to_string(),
            mean_s,
            median_s,
            std_s,
            p95_s,
            latencies,
        });
    }

    Ok(results)
}
