use criterion::{black_box, criterion_group, Criterion};
use hlcs_batch::{merkle_lattice_tree, sis_opening};
use hlcs_core::load_config;
use std::fs::File;
use std::io::Write;
use std::time::Instant;

fn generate_table() {
    let config = load_config();
    std::fs::create_dir_all("../../results/tables").unwrap();
    let mut file = File::create("../../results/tables/obj2_scaling.csv").unwrap();
    writeln!(file, "batch_size,proof_size_bytes,verification_time_ms").unwrap();

    let batch_sizes = &config.batching.max_order_batch_sizes;

    for &size in batch_sizes {
        let messages: Vec<Vec<u8>> = (0..size).map(|i| format!("msg{}", i).into_bytes()).collect();
        let indices: Vec<usize> = (0..std::cmp::min(10, size)).collect();
        let target_messages: Vec<Vec<u8>> = indices.iter().map(|&i| messages[i].clone()).collect();

        let tree = merkle_lattice_tree::build_tree(&messages);
        let proof = sis_opening::generate_multi_proof(&tree, &indices);
        let proof_size = proof.proof_data.len();

        let start = Instant::now();
        let mut iters = 0;
        let bench_duration = std::time::Duration::from_millis(500); // Quick benchmark loop

        while start.elapsed() < bench_duration {
            black_box(sis_opening::verify_multi_proof(&tree.root, &proof, &target_messages, &indices));
            iters += 1;
        }

        let total_time = start.elapsed();
        let verify_time_ms = total_time.as_secs_f64() * 1000.0 / (iters as f64);

        writeln!(file, "{},{},{:.4}", size, proof_size, verify_time_ms).unwrap();
    }
}

pub fn dummy_bench(c: &mut Criterion) {
    c.bench_function("dummy", |b| b.iter(|| {}));
}
criterion_group!(benches, dummy_bench);

fn main() {
    generate_table();
}
