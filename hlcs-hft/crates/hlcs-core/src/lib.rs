pub mod hash_commit;
pub mod lattice_commit;
pub mod hybrid;
pub mod constant_time;

use serde::Deserialize;

#[derive(Deserialize, Debug)]
pub struct ReproducibilityConfig {
    pub global_seed: u64,
    pub bootstrap_resamples: usize,
    pub significance_alpha: f64,
}

#[derive(Deserialize, Debug)]
pub struct LatticeConfig {
    pub security_category: usize,
    pub lwe_dimension: usize,
    pub module_rank: usize,
}

#[derive(Deserialize, Debug)]
pub struct HashConfig {
    pub algorithm: String,
    pub keccak_rounds: usize,
}

#[derive(Deserialize, Debug)]
pub struct LatencyTargetsConfig {
    pub baseline_hash_only: f64,
    pub baseline_lattice_only: f64,
    pub hybrid_v1_low: f64,
    pub hybrid_v1_high: f64,
    pub proposed_target: f64,
}

#[derive(Deserialize, Debug)]
pub struct BatchingConfig {
    pub max_order_batch_sizes: Vec<usize>,
    pub tree_arity: usize,
}

#[derive(Deserialize, Debug)]
pub struct StarkConfig {
    pub target_security_bits: usize,
    pub fri_blowup_factor: usize,
    pub fri_folding_factor: usize,
}

#[derive(Deserialize, Debug)]
pub struct MarketDataConfig {
    pub instrument: String,
    pub tick_source: String,
    pub date_range_start: String,
    pub date_range_end: String,
    pub lobster_ticker: String,
}

#[derive(Deserialize, Debug)]
pub struct ExperimentConfig {
    pub reproducibility: ReproducibilityConfig,
    pub lattice: LatticeConfig,
    pub hash: HashConfig,
    pub batching: BatchingConfig,
    pub stark: StarkConfig,
    pub market_data: MarketDataConfig,
    pub latency_targets_ms: LatencyTargetsConfig,
}

pub fn load_config() -> ExperimentConfig {
    let config_str = std::fs::read_to_string("../../config/experiment.toml")
        .unwrap_or_else(|_| std::fs::read_to_string("config/experiment.toml").expect("Could not find config/experiment.toml"));
    toml::from_str(&config_str).expect("Failed to parse config")
}
