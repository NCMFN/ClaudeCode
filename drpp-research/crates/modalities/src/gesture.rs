use rand::rngs::StdRng;
use rand_distr::{Distribution, Normal};

/// Generates a set of gesture features.
/// 21 features = 12 xyz trajectory + 6 velocity + 3 depth
pub fn generate_sample(is_legitimate: bool, noise_level: f64, rng: &mut StdRng) -> Vec<f64> {
    let mut features = Vec::with_capacity(21);

    let (x_mean, x_std) = (0.0, 1.0);
    let (v_mean, v_std) = (0.5, 0.2);
    let (d_mean, d_std) = if is_legitimate {
        (0.4, 0.1)
    } else {
        (0.0, 0.01)
    };

    let x_std = x_std * (1.0 + noise_level);
    let v_std = v_std * (1.0 + noise_level);
    let d_std = d_std * (1.0 + noise_level);

    let dist_x = Normal::new(x_mean, x_std).unwrap();
    let dist_v = Normal::new(v_mean, v_std).unwrap();
    let dist_d = Normal::new(d_mean, d_std).unwrap();

    for _ in 0..12 {
        features.push(dist_x.sample(rng));
    }
    for _ in 0..6 {
        features.push(dist_v.sample(rng));
    }
    for _ in 0..3 {
        features.push(dist_d.sample(rng));
    }

    features
}
