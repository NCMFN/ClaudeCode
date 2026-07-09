// Malicious security model vs honest-but-curious

pub fn honest_but_curious_verify(proof_transcript: &[u8], expected: &[u8]) -> bool {
    // A naive verification might just check if the transcript contains the expected value
    // This is vulnerable to an attacker who injects the expected value into a garbage transcript
    proof_transcript.windows(expected.len()).any(|w| w == expected)
}

pub fn malicious_secure_verify(proof_transcript: &[u8], expected: &[u8]) -> bool {
    // A hardened verification checks a cryptographic binding (e.g., a STARK proof validity)
    // We simulate this by requiring a specific structure, not just a substring match.
    // Let's say a valid transcript must exactly start with expected and end with a known suffix.
    if proof_transcript.len() < expected.len() + 4 {
        return false;
    }

    let starts_with = &proof_transcript[0..expected.len()] == expected;
    let ends_with = &proof_transcript[proof_transcript.len() - 4..] == b"DONE";

    starts_with && ends_with
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_malicious_security() {
        let expected = b"secret_value";

        // Attacker creates a garbage transcript but embeds the expected value
        let mut attack_transcript = b"garbage_data_".to_vec();
        attack_transcript.extend_from_slice(expected);
        attack_transcript.extend_from_slice(b"_more_garbage");

        // HBC assumption is vulnerable to this specific attack
        assert!(honest_but_curious_verify(&attack_transcript, expected), "HBC should be vulnerable to injection");

        // Hardened version rejects it
        assert!(!malicious_secure_verify(&attack_transcript, expected), "Hardened version should reject injection attack");

        // Hardened version accepts valid proof
        let mut valid_transcript = expected.to_vec();
        valid_transcript.extend_from_slice(b"DONE");
        assert!(malicious_secure_verify(&valid_transcript, expected));
    }
}
