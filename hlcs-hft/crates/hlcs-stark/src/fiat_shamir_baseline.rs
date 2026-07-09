// A sequential Fiat-Shamir proof of opening
pub struct FSProof {
    pub transcript: Vec<u8>,
}

pub fn generate_fs_proof(message: &[u8], _nonce: &[u8]) -> FSProof {
    // Simulate sequential time cost (O(n))
    let mut transcript = Vec::with_capacity(message.len() * 10);
    for _ in 0..10 {
        transcript.extend_from_slice(message);
    }

    // Some sequential hashing
    let mut current = transcript.clone();
    for _ in 0..100 {
        use sha3::{Digest, Sha3_256};
        let mut hasher = Sha3_256::new();
        hasher.update(&current);
        let res = hasher.finalize();
        current = res.to_vec();
    }

    FSProof { transcript }
}
