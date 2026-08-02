def get_block_size_dbs(rtt_ms, config): return config['block_size_high_latency_bits'] if rtt_ms >= config['rtt_threshold_ms'] else config['block_size_low_latency_bits']
def get_block_size_fixed_large(rtt_ms, config): return config['block_size_low_latency_bits']
def get_block_size_fixed_small(rtt_ms, config): return config['block_size_high_latency_bits']
