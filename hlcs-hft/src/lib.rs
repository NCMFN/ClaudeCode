use digest::Digest;
use rand::Rng;
use rand_distr::{Distribution, Normal};
use sha3::Sha3_256;
use rand::rngs::StdRng;

pub const Q: i64 = 12289;
pub const Q_U32: u32 = 12289;
pub const SIGMA: f64 = 3.2;
pub const N_MAX: usize = 1024;

pub type ZqVec = Vec<i64>;

pub struct PublicParams {
    pub a: Vec<Vec<u16>>, // u16 = 2x cache density vs i64
    pub n: usize,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Commitment {
    pub c1: [u8; 32],
    pub c2: ZqVec,
}

#[derive(Clone, Debug)]
pub struct OpeningHint {
    pub r: ZqVec,
    pub e: ZqVec,
    pub m: Vec<u8>,
}

// ── Setup: cache-friendly row-major u16 ──
pub fn setup<R: Rng>(rng: &mut R, n: usize) -> PublicParams {
    let a = (0..n)
       .map(|_| (0..n).map(|_| rng.gen_range(0..Q_U32) as u16).collect())
       .collect();
    PublicParams { a, n }
}

pub fn encode(m: &[u8], n: usize) -> ZqVec {
    let digest = Sha3_256::digest(m);
    let half_q = Q / 2;
    let mut v = vec![0i64; n];
    for (i, byte) in digest.iter().enumerate() {
        for bit in 0..8 {
            let idx = i * 8 + bit;
            if idx >= n { return v; }
            if (byte >> bit) & 1 == 1 { v[idx] = half_q; }
        }
    }
    v
}

#[inline(always)]
pub fn sample_error<R: Rng>(rng: &mut R, n: usize) -> ZqVec {
    let dist = Normal::new(0.0, SIGMA).unwrap();
    let mut v = Vec::with_capacity(n);
    for _ in 0..n {
        // Centered around 0, keep in [0,q) for fast mod
        let e = dist.sample(rng).round() as i64;
        v.push(e.rem_euclid(Q));
    }
    v
}

#[inline(always)]
pub fn sample_uniform<R: Rng>(rng: &mut R, n: usize) -> ZqVec {
    (0..n).map(|_| rng.gen_range(0..Q) as i64).collect()
}

// ── HFT FAST PATH: blocked mat-vec, u32 accum, single mod ──
#[inline(always)]
pub fn mat_vec_mul_fast(a: &[Vec<u16>], v: &[i64], out: &mut [i64]) {
    let n = a.len();
    // Block size 64 = L1 cache friendly
    const BLOCK: usize = 64;
    for i in 0..n { out[i] = 0; }

    for i in 0..n {
        let mut acc: u32 = 0;
        let row = &a[i];
        // Unrolled inner loop, accumulate in u32 then mod once
        let mut j = 0;
        while j + 4 <= n {
            acc += row[j] as u32 * v[j] as u32;
            acc += row[j+1] as u32 * v[j+1] as u32;
            acc += row[j+2] as u32 * v[j+2] as u32;
            acc += row[j+3] as u32 * v[j+3] as u32;
            if acc >= 1<<30 { acc %= Q_U32; } // prevent overflow
            j += 4;
        }
        while j < n {
            acc += row[j] as u32 * v[j] as u32;
            j += 1;
        }
        out[i] = (acc % Q_U32) as i64;
    }
}

// Add helper to generate r,e for proof (expose from commit)
pub fn sample_re(pp: &PublicParams, rng: &mut StdRng) -> (Vec<u16>, Vec<u16>) {
    let mut r = vec![0u16; pp.n]; let mut e = vec![0u16; pp.n];
    for i in 0..pp.n { r[i] = (rng.gen_range(0..u32::MAX) % Q as u32) as u16; e[i] = (rng.gen_range(0..u32::MAX) % 7) as u16; }
    (r,e)
}

// Needed for ZK
#[inline(always)]
pub fn mat_vec_mul_fast_u16(a: &[Vec<u16>], v: &[u16], out: &mut [u16]) {
    let n = a.len();
    for i in 0..n { out[i] = 0; }

    for i in 0..n {
        let mut acc: u32 = 0;
        let row = &a[i];
        let mut j = 0;
        while j + 4 <= n {
            acc += row[j] as u32 * v[j] as u32;
            acc += row[j+1] as u32 * v[j+1] as u32;
            acc += row[j+2] as u32 * v[j+2] as u32;
            acc += row[j+3] as u32 * v[j+3] as u32;
            if acc >= 1<<30 { acc %= Q_U32; }
            j += 4;
        }
        while j < n {
            acc += row[j] as u32 * v[j] as u32;
            j += 1;
        }
        out[i] = (acc % Q_U32) as u16;
    }
}

#[inline(always)]
pub fn add_vec_mod_q_u16(out: &mut [u16], a: &[u16], b: &[u16]) {
    for i in 0..out.len() {
        out[i] = ((a[i] as u32 + b[i] as u32) % Q_U32) as u16;
    }
}

#[inline(always)]
pub fn vec_add_mod_fast(a: &[i64], b: &[i64], c: &[i64], out: &mut [i64]) {
    for i in 0..a.len() {
        let mut s = a[i] + b[i] + c[i];
        s %= Q;
        if s < 0 { s += Q; }
        out[i] = s;
    }
}

pub fn hash_r(r: &ZqVec) -> [u8; 32] {
    let mut h = Sha3_256::new();
    for &x in r { h.update((x as u16).to_le_bytes()); }
    h.finalize().into()
}

// ── Commit: zero-alloc version ──
pub fn commit<R: Rng>(pp: &PublicParams, m: &[u8], rng: &mut R, buf_ar: &mut ZqVec, buf_c2: &mut ZqVec) -> (Commitment, OpeningHint) {
    let r = sample_uniform(rng, pp.n);
    let e = sample_error(rng, pp.n);
    let c1 = hash_r(&r);

    mat_vec_mul_fast(&pp.a, &r, buf_ar);
    let em = encode(m, pp.n);
    vec_add_mod_fast(buf_ar, &em, &e, buf_c2);

    (Commitment { c1, c2: buf_c2.clone() }, OpeningHint { r, e, m: m.to_vec() })
}

// Wrapper for tests
pub fn commit_simple<R: Rng>(pp: &PublicParams, m: &[u8], rng: &mut R) -> (Commitment, OpeningHint) {
    let mut b1 = vec![0; pp.n];
    let mut b2 = vec![0; pp.n];
    commit(pp, m, rng, &mut b1, &mut b2)
}

pub fn verify(pp: &PublicParams, c: &Commitment, hint: &OpeningHint) -> bool {
    if hash_r(&hint.r)!= c.c1 { return false; }
    let mut ar = vec![0; pp.n];
    mat_vec_mul_fast(&pp.a, &hint.r, &mut ar);
    let em = encode(&hint.m, pp.n);
    let mut res = vec![0; pp.n];
    vec_add_mod_fast(&ar, &em, &hint.e, &mut res);
    res == c.c2
}

// ── keep your hash_only / lattice_only baselines unchanged ──
pub fn commit_hash_only<R: Rng>(m: &[u8], rng: &mut R) -> ([u8; 32], [u8; 32]) {
    let mut r = [0u8; 32]; rng.fill(&mut r);
    let mut h = Sha3_256::new(); h.update(m); h.update(r);
    (h.finalize().into(), r)
}
pub fn verify_hash_only(m: &[u8], c: &[u8; 32], r: &[u8; 32]) -> bool {
    let mut h = Sha3_256::new(); h.update(m); h.update(r);
    Into::<[u8; 32]>::into(h.finalize()) == *c
}

pub mod zk;
pub use zk::{prove_agg, verify_agg, ZKProofAgg, proof_size_bytes};

#[cfg(test)]
mod tests {
    use super::*; use rand::{rngs::StdRng, SeedableRng};
    fn rng() -> StdRng { StdRng::seed_from_u64(0xDEADBEEF) }
    const TEST_N: usize = 64;
    #[test] fn hft_roundtrip() {
        let mut rng = rng(); let pp = setup(&mut rng, TEST_N);
        let (c,h) = commit_simple(&pp, b"EUR/USD 1.0950", &mut rng);
        assert!(verify(&pp,&c,&h));
    }
}
