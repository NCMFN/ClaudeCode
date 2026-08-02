import math
def binary_shannon_entropy(x): return 0.0 if x <= 0 or x >= 1 else -x * math.log2(x) - (1 - x) * math.log2(1 - x)
def compute_secure_key_rate(N, E, f_E, epsilon):
    n = N / 2.0; q = 0.5
    leak_EC = n * binary_shannon_entropy(E) * f_E
    delta = 7 * math.sqrt(math.log2(2.0 / epsilon) / N)
    return max(0.0, (n / N) * (q - f_E * binary_shannon_entropy(E) - (leak_EC / n) - delta))
if __name__ == "__main__":
    assert compute_secure_key_rate(4096, 0.05, 1.16, 1e-10) == 0.0
    assert abs(compute_secure_key_rate(1000000, 0.01, 1.0, 1e-10) - 0.1487) < 0.001
