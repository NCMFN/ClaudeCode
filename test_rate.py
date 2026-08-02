import math

def H2(E):
    if E <= 0 or E >= 1: return 0
    return -E*math.log2(E) - (1-E)*math.log2(1-E)

for N in [1024, 4096]:
    for E in [0.02, 0.05]:
        eps = 1e-10
        f = 1.16
        n = N / 2.0
        q = 0.5

        leak_EC = n * H2(E) * f
        delta = 7 * math.sqrt(math.log2(2/eps) / N)
        rate = (n/N) * (q - f * H2(E) - (leak_EC/n) - delta)
        print(f"N={N}, E={E} -> rate={rate} delta={delta}")
