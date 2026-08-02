def get_block_size_dbs(rtt_ms, config):
    if rtt_ms > config["rtt_threshold_ms"]:
        return config["block_size_high_latency_bits"]
    else:
        return config["block_size_low_latency_bits"]

def get_block_size_fixed_large(rtt_ms, config):
    return config["block_size_high_latency_bits"]

def get_block_size_fixed_small(rtt_ms, config):
    return config["block_size_low_latency_bits"]
if __name__ == "__main__":
    test_config = {
        "rtt_threshold_ms": 150,
        "block_size_high_latency_bits": 1024,
        "block_size_low_latency_bits": 4096
    }
    assert get_block_size_dbs(160, test_config) == 1024
    assert get_block_size_dbs(140, test_config) == 4096
    assert get_block_size_fixed_large(160, test_config) == 1024
    assert get_block_size_fixed_small(140, test_config) == 4096
    print("dbs_policy.py verified.")
