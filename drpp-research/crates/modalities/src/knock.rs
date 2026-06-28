use rand::rngs::StdRng;
use rand_distr::{Distribution, Normal};

/// Generates a set of knock features.
/// 13 features = 5 timing (ms) + 5 force + 3 rhythm ratios
pub fn generate_sample(is_legitimate: bool, noise_level: f64, rng: &mut StdRng) -> Vec<f64> {
    let mut features = Vec::with_capacity(13);

    let (t_mean, t_std) = if is_legitimate {
        (300.0, 40.0)
    } else {
        (300.0, 3.0)
    };
    let (f_mean, f_std) = if is_legitimate {
        (0.6, 0.15)
    } else {
        (0.6, 0.02)
    };
    let (r_mean, r_std) = if is_legitimate {
        (1.0, 0.12)
    } else {
        (1.0, 0.02)
    };

    let t_std = t_std * (1.0 + noise_level);
    let f_std = f_std * (1.0 + noise_level);
    let r_std = r_std * (1.0 + noise_level);

    let dist_t = Normal::new(t_mean, t_std).unwrap();
    let dist_f = Normal::new(f_mean, f_std).unwrap();
    let dist_r = Normal::new(r_mean, r_std).unwrap();

    for _ in 0..5 {
        features.push(dist_t.sample(rng));
    }
    for _ in 0..5 {
        features.push(dist_f.sample(rng));
    }
    for _ in 0..3 {
        features.push(dist_r.sample(rng));
    }

    features
}
