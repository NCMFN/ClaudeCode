"""
Cryptographic parameter sets for HLCS.
Parameters follow CRYSTALS-Kyber (n=512, q=12289) conventions.
Reference: https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf
"""

PARAM_SETS = {
    "HLCS-128": {"n": 256,  "q": 7681,  "sigma": 3.2, "B": 16, "security_bits": 128},
    "HLCS-192": {"n": 384,  "q": 12289, "sigma": 3.2, "B": 16, "security_bits": 192},
    "HLCS-256": {"n": 512,  "q": 12289, "sigma": 3.2, "B": 16, "security_bits": 256},
    "HLCS-512": {"n": 768,  "q": 12289, "sigma": 3.2, "B": 16, "security_bits": 512},
    "HLCS-1024": {"n": 1024, "q": 40961, "sigma": 3.2, "B": 16, "security_bits": 1024},
}

DEFAULT_PARAMS = PARAM_SETS["HLCS-256"]  # Paper's primary parameter set
