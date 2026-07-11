pub struct SelectiveProof {
    pub volume_proof: Vec<u8>,
}

pub fn prove_volume_gt_threshold(exact_volume: u64, threshold: u64) -> SelectiveProof {
    // Generate a ZK proof that volume > threshold
    assert!(exact_volume > threshold);

    // We mock the proof by just producing some bytes.
    // Crucially, the exact_volume is NOT in these bytes.
    let mut proof = Vec::with_capacity(32);
    proof.extend_from_slice(&threshold.to_be_bytes());
    // Add some random-looking padding
    for i in 0..24 {
        proof.push((threshold.wrapping_add(i as u64) % 256) as u8);
    }

    SelectiveProof {
        volume_proof: proof,
    }
}

pub fn verify_volume_proof(proof: &SelectiveProof, threshold: u64) -> bool {
    if proof.volume_proof.len() < 8 {
        return false;
    }
    let mut t_bytes = [0u8; 8];
    t_bytes.copy_from_slice(&proof.volume_proof[0..8]);
    let proven_threshold = u64::from_be_bytes(t_bytes);

    proven_threshold == threshold
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_selective_disclosure() {
        let exact_volume = 1000;
        let threshold = 500;

        let proof = prove_volume_gt_threshold(exact_volume, threshold);
        assert!(verify_volume_proof(&proof, threshold));

        // Assert exact value is NOT derivable (in our mock, it's just not in the byte array)
        let exact_bytes = exact_volume.to_be_bytes();
        let mut found = false;
        for window in proof.volume_proof.windows(8) {
            if window == exact_bytes {
                found = true;
                break;
            }
        }
        assert!(!found, "Exact volume leaked in proof transcript");
    }
}
