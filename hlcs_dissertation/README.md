# Hybrid Post-Quantum Commitment Schemes for Latency-Constrained Financial Systems

## Abstract
A Hybrid Hash-Lattice Commitment Scheme (HLCS) that:
- Combines SHA3-256 hash-based commitments with LWE-based lattice commitments
- Achieves sub-millisecond latency (0.05–0.2 ms) with >=128-bit post-quantum security
- Introduces "Latency-Adaptive Security" (LAS) — a new security definition
- Extends with a non-interactive zero-knowledge proof via Fiat–Shamir transform
- Applied to high-frequency forex trading (EUR/USD) to prevent front-running

## Installation
```bash
pip install -r requirements.txt
python setup.py install
```

## Running the Experiments
```bash
cd experiments
python run_all.py
```

## Directory Structure
- `core/`: Core cryptographic algorithms implementation
- `experiments/`: Scripts for experiments 01-15
- `figures/`: PNG and PDF outputs of figures
- `tables/`: CSV and XLSX outputs of data
- `outputs/`: Consolidated output log and Excel files
- `data/`: Placeholder for data

## Output
All tables are consolidated into `outputs/dissertation_tables.xlsx`

## References
- NIST FIPS 203: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf
- CRYSTALS-Kyber: https://pq-crystals.org/kyber/data/kyber-specification-round3-20210804.pdf
- Regev LWE: https://arxiv.org/abs/2401.03703
- Zhandry QROM: https://eprint.iacr.org/2018/1245.pdf
- Fiat-Shamir NIZK: https://link.springer.com/article/10.1007/s00145-024-09534-z
- Kyber Failure Prob: https://iopscience.iop.org/article/10.1088/2632-2153/ada85a
- BKZ Attack: https://eprint.iacr.org/2020/1304.pdf
- Grover Bound: https://arxiv.org/abs/quant-ph/9605043
