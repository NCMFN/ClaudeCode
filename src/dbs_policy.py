import json

def load_config(config_path="src/config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def dbs_policy(rtt_ms, config):
    """
    Dynamic Block-Sizer (DBS) policy: piecewise step function based on RTT threshold.
    """
    if rtt_ms >= config["rtt_threshold_ms"]:
        return config["block_size_high_latency_bits"]
    else:
        return config["block_size_low_latency_bits"]

def fixed_large_policy(rtt_ms, config):
    """
    Fixed-large baseline policy.
    """
    return config["block_size_low_latency_bits"]

def fixed_small_policy(rtt_ms, config):
    """
    Fixed-small baseline policy.
    """
    return config["block_size_high_latency_bits"]
