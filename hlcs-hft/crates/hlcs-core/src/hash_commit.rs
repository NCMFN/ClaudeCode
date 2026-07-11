use sha3::{Digest, Sha3_256};
use rand::Rng;

pub struct HashCommitment {
    pub commitment: [u8; 32],
    pub opening_info: Vec<u8>, // Contains the nonce
}

pub fn commit(message: &[u8]) -> HashCommitment {
    let mut rng = rand::thread_rng();
    let mut nonce = [0u8; 32];
    rng.fill(&mut nonce);
    commit_with_nonce(message, &nonce)
}

pub fn commit_with_nonce(message: &[u8], nonce: &[u8; 32]) -> HashCommitment {
    let mut hasher = Sha3_256::new();
    hasher.update(message);
    hasher.update(nonce);
    let result = hasher.finalize();
    let mut commitment = [0u8; 32];
    commitment.copy_from_slice(&result);

    HashCommitment {
        commitment,
        opening_info: nonce.to_vec(),
    }
}

pub fn verify(commitment: &[u8; 32], message: &[u8], opening_info: &[u8]) -> bool {
    if opening_info.len() != 32 {
        return false;
    }
    let mut nonce = [0u8; 32];
    nonce.copy_from_slice(opening_info);

    let expected = commit_with_nonce(message, &nonce);
    commitment == &expected.commitment
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_commit_verify() {
        let msg = b"test order message";
        let commit = commit(msg);
        assert!(verify(&commit.commitment, msg, &commit.opening_info));
    }

    #[test]
    fn test_verify_fail() {
        let msg1 = b"test order message 1";
        let msg2 = b"test order message 2";
        let commit = commit(msg1);
        assert!(!verify(&commit.commitment, msg2, &commit.opening_info));
    }

    #[test]
    fn test_known_vector() {
        let msg = b"abc";
        let nonce = [0u8; 32];
        let commit = commit_with_nonce(msg, &nonce);

        // This is not a formal KAT, but a known value test for Sha3-256(msg||nonce)
        // Sha3-256("abc" || 32 zero bytes)
        let mut hasher = Sha3_256::new();
        hasher.update(msg);
        hasher.update(nonce);
        let expected = hasher.finalize();

        let mut expected_arr = [0u8; 32];
        expected_arr.copy_from_slice(&expected);
        assert_eq!(commit.commitment, expected_arr);
    }
}
