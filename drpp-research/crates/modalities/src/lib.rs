pub mod classifier;
pub mod gesture;
pub mod knock;
pub mod touch;

use rand::rngs::StdRng;

pub fn generate_dataset<F>(
    n_legit: usize,
    n_spoofed: usize,
    noise_level: f64,
    mut rng: StdRng,
    generator: F,
) -> (Vec<Vec<f64>>, Vec<bool>)
where
    F: Fn(bool, f64, &mut StdRng) -> Vec<f64>,
{
    let mut features = Vec::with_capacity(n_legit + n_spoofed);
    let mut labels = Vec::with_capacity(n_legit + n_spoofed);

    for _ in 0..n_legit {
        features.push(generator(true, noise_level, &mut rng));
        labels.push(true);
    }

    for _ in 0..n_spoofed {
        features.push(generator(false, noise_level, &mut rng));
        labels.push(false);
    }

    (features, labels)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;

    #[test]
    fn test_knock_separation() {
        let mut rng1 = StdRng::seed_from_u64(42);
        let mut rng2 = StdRng::seed_from_u64(43);
        let legit = knock::generate_sample(true, 0.0, &mut rng1);
        let spoof = knock::generate_sample(false, 0.0, &mut rng2);

        // Features 0-4 are timing. Legit has variance 40^2, spoof has 3^2
        // Just verify lengths for now, deeper separation tests could check variances
        assert_eq!(legit.len(), 13);
        assert_eq!(spoof.len(), 13);
    }
}
