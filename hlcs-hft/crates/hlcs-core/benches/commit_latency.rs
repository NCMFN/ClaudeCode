use criterion::{black_box, criterion_group, Criterion};
use hlcs_core::{hash_commit, lattice_commit, hybrid, load_config};
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use std::fs::File;
use std::io::Write;

fn commit_benchmark(c: &mut Criterion) {
    let config = load_config();
    let mut rng = ChaCha8Rng::seed_from_u64(config.reproducibility.global_seed);

    let mut message = vec![0u8; 128]; // e.g., an order message size
    rng.fill(&mut message[..]);

    let mut group = c.benchmark_group("Commitments");

    group.bench_function("Hash Commitment", |b| {
        b.iter(|| hash_commit::commit(black_box(&message)))
    });

    group.bench_function("Lattice Commitment proxy", |b| {
        b.iter(|| lattice_commit::commit(black_box(&message)))
    });

    group.bench_function("Hybrid Commitment", |b| {
        b.iter(|| hybrid::commit(black_box(&message)))
    });

    group.finish();
}

fn bootstrap_confidence_interval(data: &[f64], n_resamples: usize, alpha: f64, seed: u64) -> (f64, f64, f64, f64) {
    if data.is_empty() { return (0.0, 0.0, 0.0, 0.0); }
    let mut rng = ChaCha8Rng::seed_from_u64(seed);

    let original_mean = data.iter().sum::<f64>() / data.len() as f64;
    let variance = data.iter().map(|&x| (x - original_mean).powi(2)).sum::<f64>() / (data.len() - 1) as f64;
    let original_std = variance.sqrt();

    let mut resample_means = Vec::with_capacity(n_resamples);
    for _ in 0..n_resamples {
        let mut sample_sum = 0.0;
        for _ in 0..data.len() {
            let idx = rng.gen_range(0..data.len());
            sample_sum += data[idx];
        }
        resample_means.push(sample_sum / data.len() as f64);
    }

    resample_means.sort_by(|a, b| a.partial_cmp(b).unwrap());

    let lower_idx = (n_resamples as f64 * (alpha / 2.0)) as usize;
    let upper_idx = (n_resamples as f64 * (1.0 - alpha / 2.0)) as usize;

    let ci_low = resample_means[lower_idx.min(n_resamples - 1)];
    let ci_high = resample_means[upper_idx.min(n_resamples - 1)];

    (original_mean, original_std, ci_low, ci_high)
}

fn generate_table() {
    let config = load_config();
    let n = config.reproducibility.bootstrap_resamples;
    let seed = config.reproducibility.global_seed;
    let alpha = config.reproducibility.significance_alpha;

    std::fs::create_dir_all("../../results/tables").unwrap();
    let mut file = File::create("../../results/tables/obj1_latency.csv").unwrap();
    writeln!(file, "scheme,mean_ms,std_ms,n,ci95_low,ci95_high").unwrap();

    // We run a mini benchmark to gather real data points for the table
    let mut rng = ChaCha8Rng::seed_from_u64(seed);
    let mut message = vec![0u8; 128];
    rng.fill(&mut message[..]);

    let sample_size = 1000;

    // Hash
    let mut hash_times = Vec::with_capacity(sample_size);
    for _ in 0..sample_size {
        let start = std::time::Instant::now();
        criterion::black_box(hash_commit::commit(&message));
        hash_times.push(start.elapsed().as_secs_f64() * 1000.0);
    }
    let (h_mean, h_std, h_low, h_high) = bootstrap_confidence_interval(&hash_times, n, alpha, seed);
    writeln!(file, "hash,{:.4},{:.4},{},{:.4},{:.4}", h_mean, h_std, n, h_low, h_high).unwrap();

    // Lattice (Proxy)
    let mut lattice_times = Vec::with_capacity(sample_size);
    for _ in 0..sample_size {
        let start = std::time::Instant::now();
        criterion::black_box(lattice_commit::commit(&message));
        lattice_times.push(start.elapsed().as_secs_f64() * 1000.0);
    }
    let (l_mean, l_std, l_low, l_high) = bootstrap_confidence_interval(&lattice_times, n, alpha, seed);
    writeln!(file, "lattice_proxy,{:.4},{:.4},{},{:.4},{:.4}", l_mean, l_std, n, l_low, l_high).unwrap();

    // Hybrid
    let mut hybrid_times = Vec::with_capacity(sample_size);
    for _ in 0..sample_size {
        let start = std::time::Instant::now();
        criterion::black_box(hybrid::commit(&message));
        hybrid_times.push(start.elapsed().as_secs_f64() * 1000.0);
    }
    let (hy_mean, hy_std, hy_low, hy_high) = bootstrap_confidence_interval(&hybrid_times, n, alpha, seed);
    writeln!(file, "hybrid_proxy,{:.4},{:.4},{},{:.4},{:.4}", hy_mean, hy_std, n, hy_low, hy_high).unwrap();
}

criterion_group!(benches, commit_benchmark);

fn main() {
    generate_table();
    // To run standard benches:
    // benches();
}
