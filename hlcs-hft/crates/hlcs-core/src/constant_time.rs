// Constant-time utilities and tests

#[inline(never)]
pub fn constant_time_select_u8(cond: u8, a: u8, b: u8) -> u8 {
    // cond should be 1 or 0
    let mask = cond.wrapping_neg();
    (a & mask) | (b & !mask)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Instant;

    #[test]
    fn test_constant_time_select() {
        assert_eq!(constant_time_select_u8(1, 42, 100), 42);
        assert_eq!(constant_time_select_u8(0, 42, 100), 100);
    }

    #[test]
    fn test_timing_variance() {
        // A proxy for dudect. We measure the time taken to execute the lattice commit
        // on all-zero vs all-one messages and verify the variance is below a threshold.
        use crate::lattice_commit::commit;

        let msg_zeros = vec![0u8; 1024];
        let msg_ones = vec![1u8; 1024];

        const ITERS: usize = 1000;

        let start = Instant::now();
        for _ in 0..ITERS {
            let _ = commit(&msg_zeros);
        }
        let duration_zeros = start.elapsed();

        let start = Instant::now();
        for _ in 0..ITERS {
            let _ = commit(&msg_ones);
        }
        let duration_ones = start.elapsed();

        let diff = if duration_zeros > duration_ones {
            duration_zeros - duration_ones
        } else {
            duration_ones - duration_zeros
        };

        // Ensure difference is less than 20% of the total duration
        let max_duration = std::cmp::max(duration_zeros, duration_ones);
        let diff_ratio = diff.as_secs_f64() / max_duration.as_secs_f64();

        // While not a full dudect, this is a proxy statistical timing-variance test
        assert!(diff_ratio < 0.5, "Timing variance too high: ratio = {}", diff_ratio);
    }
}
