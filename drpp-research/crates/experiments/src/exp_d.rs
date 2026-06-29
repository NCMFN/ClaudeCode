#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::Config;
use anyhow::Result;
use modalities::classifier::{
    evaluate_classifier, train_test_split, ConfusionMatrix, GaussianNaiveBayes, LogisticRegression,
    Metrics, Point,
};
use modalities::{generate_dataset, gesture, knock, touch};
use rand::rngs::StdRng;
use rand::SeedableRng;
use rayon::prelude::*;

#[derive(Debug, Clone)]
pub struct ModalityResult {
    pub modality: String,
    pub classifier: String,
    pub noise_level: f64,
    pub metrics: Metrics,
    pub cm: ConfusionMatrix,
    pub roc_curve: Vec<Point>,
}

pub fn run(cfg: &Config) -> Result<Vec<ModalityResult>> {
    println!("Running Experiment D: Classifier Metrics vs Noise...");

    let modalities = vec!["knock", "touch", "gesture"];
    let classifiers = vec!["LR", "GNB"];

    // Create parameter sweep combinations
    let mut params = Vec::new();
    for m in &modalities {
        for &noise in &cfg.noise_levels {
            for c in &classifiers {
                params.push((m.to_string(), noise, c.to_string()));
            }
        }
    }

    let results: Vec<ModalityResult> = params
        .into_par_iter()
        .map(|(modality, noise, classifier_name)| {
            let mut rng = StdRng::seed_from_u64(cfg.seed + (noise * 1000.0) as u64);

            // Generate dataset based on modality
            let (features, labels) = match modality.as_str() {
                "knock" => generate_dataset(
                    cfg.modality_samples / 2,
                    cfg.modality_samples / 2,
                    noise,
                    rng.clone(),
                    knock::generate_sample,
                ),
                "touch" => generate_dataset(
                    cfg.modality_samples / 2,
                    cfg.modality_samples / 2,
                    noise,
                    rng.clone(),
                    touch::generate_sample,
                ),
                "gesture" => generate_dataset(
                    cfg.modality_samples / 2,
                    cfg.modality_samples / 2,
                    noise,
                    rng.clone(),
                    gesture::generate_sample,
                ),
                _ => panic!("Unknown modality"),
            };

            // Train/test split (70/30)
            let (tr_f, tr_l, te_f, te_l) = train_test_split(&features, &labels, 0.7, &mut rng);

            let (metrics, cm, roc_curve) = if classifier_name == "LR" {
                let model = LogisticRegression::fit(&tr_f, &tr_l);
                evaluate_classifier(&te_f, &te_l, |f| model.predict_proba(f))
            } else {
                let model = GaussianNaiveBayes::fit(&tr_f, &tr_l);
                evaluate_classifier(&te_f, &te_l, |f| model.predict_proba(f))
            };

            ModalityResult {
                modality,
                classifier: classifier_name,
                noise_level: noise,
                metrics,
                cm,
                roc_curve,
            }
        })
        .collect();

    Ok(results)
}
