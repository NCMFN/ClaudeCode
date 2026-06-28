use rand::{rngs::StdRng, Rng};

/// Adversary who blindly guesses a single `k`-bit response.
pub fn single_guess(k: u32, rng: &mut StdRng) -> u64 {
    let guess = rng.gen::<u64>();
    if k >= 64 {
        guess
    } else {
        guess & ((1u64 << k) - 1)
    }
}

/// Adversary group of `n` colluders who each make one independent guess.
/// Returns a list of all their guesses.
pub fn collusion_guesses(k: u32, n: usize, rng: &mut StdRng) -> Vec<u64> {
    let mut guesses = Vec::with_capacity(n);
    for _ in 0..n {
        guesses.push(single_guess(k, rng));
    }
    guesses
}

/// Traditional adversary who exploits visual/environmental cues.
/// Success is determined entirely by the `deception_prob`.
pub fn traditional_adversary(deception_prob: f64, rng: &mut StdRng) -> bool {
    rng.gen::<f64>() < deception_prob
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;

    #[test]
    fn test_single_guess_bounds() {
        let mut rng = StdRng::seed_from_u64(42);
        for k in 1..=20 {
            let guess = single_guess(k, &mut rng);
            assert!(guess < (1 << k));
        }
    }

    #[test]
    fn test_collusion_guesses_bounds() {
        let mut rng = StdRng::seed_from_u64(42);
        let n = 5;
        let k = 10;
        let guesses = collusion_guesses(k, n, &mut rng);
        assert_eq!(guesses.len(), n);
        for guess in guesses {
            assert!(guess < (1 << k));
        }
    }
}
