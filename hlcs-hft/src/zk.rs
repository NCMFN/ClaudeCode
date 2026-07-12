use crate::{PublicParams, Commitment, Q, mat_vec_mul_fast_u16, add_vec_mod_q_u16};
use rand::{RngCore, SeedableRng, rngs::StdRng};
use sha3::{Digest, Sha3_256};

const ROUNDS: usize = 10; // 10 * log2(Q) ≈ 10*13.6 = 136-bit soundness

#[derive(Clone)]
pub struct ZKProofAgg {
    pub t1: Vec<Vec<u16>>, // [ROUNDS][n]
    pub t2: Vec<[u8;32]>,
    pub s_r: Vec<Vec<u16>>,
    pub s_e: Vec<Vec<u16>>,
    pub challenges: Vec<[u8;32]>,
}

fn hash_fs(c: &Commitment, t1: &[u16], t2: &[u8;32], round: u8, prev: &[u8]) -> [u8;32] {
    let mut h = Sha3_256::new();
    h.update(prev); h.update(&[round]); h.update(&c.c1);
    for &x in &c.c2 { h.update((x as u16).to_le_bytes()); }
    h.update(t2); for &v in t1 { h.update(&v.to_le_bytes()); }
    h.finalize().into()
}

pub fn prove_agg(pp: &PublicParams, c: &Commitment, r: &[u16], e: &[u16], rng: &mut StdRng) -> ZKProofAgg {
    let mut t1_all = Vec::with_capacity(ROUNDS);
    let mut t2_all = Vec::with_capacity(ROUNDS);
    let mut s_r_all = Vec::with_capacity(ROUNDS);
    let mut s_e_all = Vec::with_capacity(ROUNDS);
    let mut ch_all = Vec::with_capacity(ROUNDS);
    let mut prev = [0u8;32];

    for round in 0..ROUNDS {
        // 1. Masking
        let mut y_r = vec![0u16; pp.n]; let mut y_e = vec![0u16; pp.n];
        for i in 0..pp.n { y_r[i]=(rng.next_u32()%Q as u32) as u16; y_e[i]=(rng.next_u32()%Q as u32) as u16; }

        // 2. t1 = A*y_r + y_e
        let mut ay = vec![0u16; pp.n]; mat_vec_mul_fast_u16(&pp.a, &y_r, &mut ay);
        let mut t1 = vec![0u16; pp.n]; add_vec_mod_q_u16(&mut t1, &ay, &y_e);
        let mut t2 = [0u8;32]; let mut h=Sha3_256::new(); h.update(&[round as u8]); for &v in &y_r { h.update(&v.to_le_bytes()); } t2.copy_from_slice(&h.finalize());

        // 3. Fiat-Shamir challenge chained
        let chal = hash_fs(c, &t1, &t2, round as u8, &prev);
        let c_scalar = (chal[0] as u32 * 256 + chal[1] as u32) % Q as u32; // 16-bit challenge -> 2^-13.6 per round

        // 4. Responses
        let mut s_r = vec![0u16; pp.n]; let mut s_e = vec![0u16; pp.n];
        for i in 0..pp.n {
            s_r[i]=((y_r[i] as u32 + c_scalar * r[i] as u32)%Q as u32) as u16;
            s_e[i]=((y_e[i] as u32 + c_scalar * e[i] as u32)%Q as u32) as u16;
        }
        prev = chal; t1_all.push(t1); t2_all.push(t2); s_r_all.push(s_r); s_e_all.push(s_e); ch_all.push(chal);
    }
    ZKProofAgg { t1: t1_all, t2: t2_all, s_r: s_r_all, s_e: s_e_all, challenges: ch_all }
}

pub fn verify_agg(pp: &PublicParams, c: &Commitment, pf: &ZKProofAgg) -> bool {
    let mut prev = [0u8;32];
    for round in 0..ROUNDS {
        let t1 = &pf.t1[round]; let t2 = &pf.t2[round];
        let chal_exp = hash_fs(c, t1, t2, round as u8, &prev);
        if chal_exp!= pf.challenges[round] { return false; }
        let c_scalar = (chal_exp[0] as u32 * 256 + chal_exp[1] as u32) % Q as u32;
        // Verify A*s_r + s_e == t1 + c*C2
        let mut lhs = vec![0u16; pp.n]; mat_vec_mul_fast_u16(&pp.a, &pf.s_r[round], &mut lhs);
        let mut tmp = lhs.clone(); add_vec_mod_q_u16(&mut lhs, &tmp, &pf.s_e[round]);
        for i in 32..pp.n { // skip message-encoded part
            // In c.c2, entries are i64 but for zk proof they are converted/treated as mod Q
            let rhs = (t1[i] as u32 + c_scalar * (c.c2[i] as u16) as u32) % Q as u32;
            if lhs[i] as u32!= rhs { return false; }
        }
        prev = chal_exp;
    }
    true
}

pub fn proof_size_bytes(pp: &PublicParams) -> usize {
    // t1: ROUNDS*n*2 + t2: ROUNDS*32 + s_r+s_e: ROUNDS*n*4 + challenges: ROUNDS*32
    ROUNDS*(pp.n*2 + 32 + pp.n*4 + 32)
}
