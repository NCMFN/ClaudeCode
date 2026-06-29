use rand::rngs::StdRng;
use rand_distr::{Distribution, Normal};

/// Generates a set of touch features.
/// 12 features = 8 capacitance + 4 contact-area
pub fn generate_sample(is_legitimate: bool, noise_level: f64, rng: &mut StdRng) -> Vec<f64> {
    let mut features = Vec::with_capacity(12);

    let (c_mean, c_std) = if is_legitimate {
        (150.0, 20.0)
    } else {
        (200.0, 5.0)
    };
    let (a_mean, a_std) = if is_legitimate {
        (2.5, 0.5)
    } else {
        (3.5, 0.1)
    };

    let c_std = c_std * (1.0 + noise_level);
    let a_std = a_std * (1.0 + noise_level);

    let dist_c = Normal::new(c_mean, c_std).unwrap();
    let dist_a = Normal::new(a_mean, a_std).unwrap();

    for _ in 0..8 {
        features.push(dist_c.sample(rng));
    }
    for _ in 0..4 {
        features.push(dist_a.sample(rng));
    }

    features
}
