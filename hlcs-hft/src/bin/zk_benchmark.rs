use hlcs_hft::{setup, prove_agg, verify_agg, proof_size_bytes};
use rand::{SeedableRng, rngs::StdRng};
use std::time::Instant;
use std::fs;
use std::io::Write;
use std::fs::OpenOptions;

fn update_manifest(file_path: &str, description: &str, asset_type: &str) {
    let mut manifest = OpenOptions::new()
        .create(true)
        .append(true)
        .open("/app/outputs/paper_assets_manifest.csv")
        .unwrap();

    let metadata = fs::metadata("/app/outputs/paper_assets_manifest.csv").unwrap();
    if metadata.len() == 0 {
        writeln!(manifest, "file_path,description,asset_type").unwrap();
    }

    writeln!(manifest, "{},{},{}", file_path, description, asset_type).unwrap();
}

fn main() {
    fs::create_dir_all("/app/outputs/tables").unwrap();
    let path = "/app/outputs/tables/zk_proof.csv";
    let mut f = fs::File::create(path).unwrap();

    let mut rng = StdRng::seed_from_u64(42);
    println!("n,prove_ms,verify_ms,proof_KB,soundness_bits,ok");
    writeln!(f, "n,prove_ms,verify_ms,proof_KB,soundness_bits,ok").unwrap();
    for &n in &[128,256,512,768,1024] {
        let pp = setup(&mut rng, n);
        let c = hlcs_hft::Commitment{ c1:[0u8;32], c2: vec![1i64;n] };
        let r = vec![1u16;n]; let e = vec![0u16;n];
        let s = Instant::now(); let pf = prove_agg(&pp, &c, &r, &e, &mut rng); let pt=s.elapsed().as_micros() as f64/1000.0;
        let s = Instant::now(); let ok = verify_agg(&pp, &c, &pf); let vt=s.elapsed().as_micros() as f64/1000.0;
        println!("{},{:.3},{:.3},{:.1},{},{}", n, pt, vt, proof_size_bytes(&pp) as f64/1024.0, 136, ok);
        writeln!(f, "{},{:.3},{:.3},{:.1},{},{}", n, pt, vt, proof_size_bytes(&pp) as f64/1024.0, 136, ok).unwrap();
    }
    update_manifest(path, "ZK Proof Benchmark", "table");
}
