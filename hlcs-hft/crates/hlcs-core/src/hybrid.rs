use crate::hash_commit;
use crate::lattice_commit;

pub struct HybridCommitment {
    pub hash_part: hash_commit::HashCommitment,
    pub lattice_part: lattice_commit::LatticeCommitment,
}

pub fn commit(message: &[u8]) -> HybridCommitment {
    let hash_part = hash_commit::commit(message);
    let lattice_part = lattice_commit::commit(message);

    HybridCommitment {
        hash_part,
        lattice_part,
    }
}

pub fn verify(commitment: &HybridCommitment, message: &[u8]) -> bool {
    let hash_ok = hash_commit::verify(&commitment.hash_part.commitment, message, &commitment.hash_part.opening_info);
    let lattice_ok = lattice_commit::verify(&commitment.lattice_part.commitment, message, &commitment.lattice_part.opening_info);

    hash_ok && lattice_ok
}
