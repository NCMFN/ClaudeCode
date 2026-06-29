use crate::protocol::DrppGame;
use rand::rngs::StdRng;
use rand::SeedableRng;

/// Computes the Geometric Cumulative Distribution Function (CDF).
/// Returns a vector of (num_guesses, cumulative_probability) for up to `max_guesses`.
/// `p` is the probability of success on a single trial (e.g., 2^-k).
pub fn geometric_cdf(p: f64, max_guesses: u64) -> Vec<(u64, f64)> {
    let mut cdf = Vec::with_capacity(max_guesses as usize);
    for n in 1..=max_guesses {
        let prob = 1.0 - (1.0 - p).powi(n as i32);
        cdf.push((n, prob));
    }
    cdf
}

#[derive(Debug, Clone)]
pub struct ConvergencePoint {
    pub n_trials: u64,
    pub p_simulated: f64,
    pub p_theoretical: f64,
}

/// Runs a series of games to show convergence to the theoretical probability
/// as the number of trials increases.
pub fn convergence_series(
    k: u32,
    secret: &[u8],
    trial_counts: &[u64],
    seed: u64,
) -> Vec<ConvergencePoint> {
    let mut results = Vec::with_capacity(trial_counts.len());
    let rng = StdRng::seed_from_u64(seed);

    for &n_trials in trial_counts {
        let mut game = DrppGame {
            k,
            secret: secret.to_vec(),
            rng: rng.clone(), // Clone to isolate the RNG state per trial count run, optional but deterministic
        };
        let res = game.run(n_trials);
        results.push(ConvergencePoint {
            n_trials,
            p_simulated: res.p_attack_simulated,
            p_theoretical: res.p_attack_theoretical,
        });
    }

    results
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_geometric_cdf() {
        let p = 0.5; // k=1
        let cdf = geometric_cdf(p, 3);
        assert_eq!(cdf.len(), 3);
        assert_eq!(cdf[0].1, 0.5); // 1 - (1-0.5)^1
        assert_eq!(cdf[1].1, 0.75); // 1 - (1-0.5)^2
        assert_eq!(cdf[2].1, 0.875); // 1 - (1-0.5)^3
    }
}
