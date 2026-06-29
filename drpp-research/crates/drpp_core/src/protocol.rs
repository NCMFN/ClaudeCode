use hmac::{Hmac, Mac};
use rand::{rngs::StdRng, Rng};
use sha2::Sha256;

/// Type alias for HMAC-SHA256
type HmacSha256 = Hmac<Sha256>;

/// Generates a uniformly random k-bit challenge.
/// The result is packed into a `Vec<u8>`.
pub fn generate_challenge(k: u32, rng: &mut StdRng) -> Vec<u8> {
    let bytes = k.div_ceil(8) as usize;
    let mut challenge = vec![0u8; bytes];
    rng.fill(&mut challenge[..]);

    // Mask out the upper bits of the most significant byte if k is not a multiple of 8
    let r = k % 8;
    if r > 0 {
        challenge[bytes - 1] &= (1 << r) - 1;
    }

    challenge
}

/// Computes the HMAC-SHA256 of `challenge` keyed with `secret`,
/// truncating the result to `k` bits and returning it as a `u64`.
pub fn prf_response(challenge: &[u8], secret: &[u8], k: u32) -> u64 {
    let mut mac = HmacSha256::new_from_slice(secret).expect("HMAC can take key of any size");
    mac.update(challenge);
    let result = mac.finalize().into_bytes();

    // Take the first 8 bytes (64 bits) to form a u64 in little-endian
    let mut buf = [0u8; 8];
    buf.copy_from_slice(&result[..8]);
    let val = u64::from_le_bytes(buf);

    // Truncate to k bits
    if k >= 64 {
        val
    } else {
        val & ((1u64 << k) - 1)
    }
}

/// Verifies if a given `response` matches the expected response for `challenge`
/// keyed with `secret`, truncated to `k` bits.
pub fn verify(challenge: &[u8], response: u64, secret: &[u8], k: u32) -> bool {
    prf_response(challenge, secret, k) == response
}

/// Represents the results of running the DRPP game for a number of trials.
#[derive(Debug, Clone)]
pub struct GameResult {
    pub successes: u64,
    pub p_attack_simulated: f64,
    pub p_attack_theoretical: f64,
}

/// Represents a single instance of the DRPP game.
pub struct DrppGame {
    pub k: u32,
    pub secret: Vec<u8>,
    pub rng: StdRng,
}

impl DrppGame {
    /// Runs the game `n_trials` times, returning the result.
    pub fn run(&mut self, n_trials: u64) -> GameResult {
        let mut successes = 0;
        for _ in 0..n_trials {
            // Adversary randomly guesses a response
            let guess = self.rng.gen::<u64>();
            let truncated_guess = if self.k >= 64 {
                guess
            } else {
                guess & ((1u64 << self.k) - 1)
            };

            let challenge = generate_challenge(self.k, &mut self.rng);
            if verify(&challenge, truncated_guess, &self.secret, self.k) {
                successes += 1;
            }
        }

        let p_attack_simulated = successes as f64 / n_trials as f64;
        let p_attack_theoretical = 2.0f64.powi(-(self.k as i32));

        GameResult {
            successes,
            p_attack_simulated,
            p_attack_theoretical,
        }
    }
}

/// Computes the Wilson score interval for a 95% confidence level.
pub fn confidence_interval_95(p: f64, n: u64) -> (f64, f64) {
    if n == 0 {
        return (0.0, 0.0);
    }
    let z = 1.96; // 95% confidence
    let n_f64 = n as f64;
    let denominator = 1.0 + z * z / n_f64;
    let center = (p + z * z / (2.0 * n_f64)) / denominator;
    let spread =
        z * ((p * (1.0 - p) / n_f64) + (z * z / (4.0 * n_f64 * n_f64))).sqrt() / denominator;

    (center - spread, center + spread)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;

    #[test]
    fn test_prf_deterministic() {
        let challenge = b"test_challenge";
        let secret = b"secret_key";
        let k = 16;
        let r1 = prf_response(challenge, secret, k);
        let r2 = prf_response(challenge, secret, k);
        assert_eq!(r1, r2, "Same inputs should yield the same response");
    }

    #[test]
    fn test_prf_range() {
        let challenge = b"test_challenge_range";
        let secret = b"secret_key_range";
        for k in 1..=20 {
            let r = prf_response(challenge, secret, k);
            assert!(r < (1 << k), "Response should be less than 2^k");
        }
    }

    #[test]
    fn test_verify_correct() {
        let challenge = b"challenge_verify";
        let secret = b"secret_verify";
        let k = 16;
        let r = prf_response(challenge, secret, k);
        assert!(
            verify(challenge, r, secret, k),
            "Honest prover should pass verification"
        );
    }

    #[test]
    fn test_verify_wrong() {
        let secret = b"secret_wrong";
        let k = 8;
        let p_attack_theoretical = 2.0f64.powi(-(k as i32));

        let mut rng = StdRng::seed_from_u64(42);
        let n_trials = 100_000;
        let mut successes = 0;

        for _ in 0..n_trials {
            let challenge = generate_challenge(k, &mut rng);
            let guess: u64 = rng.gen_range(0..1 << k);
            if verify(&challenge, guess, secret, k) {
                successes += 1;
            }
        }

        let p_attack_simulated = successes as f64 / n_trials as f64;
        let diff = (p_attack_simulated - p_attack_theoretical).abs();

        // Ensure that the simulated attack probability is close to the theoretical one
        assert!(
            diff < 0.01,
            "Random guess should have probability of success ~ 2^-k"
        );
    }

    #[test]
    fn test_confidence_interval() {
        let p = 0.5;
        let (lo1, hi1) = confidence_interval_95(p, 100);
        let (lo2, hi2) = confidence_interval_95(p, 1000);

        let width1 = hi1 - lo1;
        let width2 = hi2 - lo2;

        assert!(
            width2 < width1,
            "Confidence interval width should shrink as n grows"
        );
    }
}
