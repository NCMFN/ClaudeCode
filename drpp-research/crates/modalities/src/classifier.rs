#![allow(clippy::type_complexity, clippy::needless_range_loop)]
use rand::rngs::StdRng;
use rand::seq::SliceRandom;
use std::f64::consts::PI;

#[derive(Debug, Clone, Copy)]
pub struct Metrics {
    pub accuracy: f64,
    pub precision: f64,
    pub recall: f64,
    pub f1: f64,
    pub auc: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct ConfusionMatrix {
    pub tn: u32,
    pub fp: u32,
    pub fn_val: u32,
    pub tp: u32,
}

#[derive(Debug, Clone)]
pub struct Point {
    pub threshold: f64,
    pub far: f64,
    pub frr: f64,
    pub tpr: f64,
    pub fpr: f64,
}

/// Computes confusion matrix and basic metrics.
fn compute_cm(predictions: &[bool], labels: &[bool]) -> ConfusionMatrix {
    let mut cm = ConfusionMatrix {
        tn: 0,
        fp: 0,
        fn_val: 0,
        tp: 0,
    };
    for (&p, &l) in predictions.iter().zip(labels.iter()) {
        match (p, l) {
            (true, true) => cm.tp += 1,
            (true, false) => cm.fp += 1,
            (false, true) => cm.fn_val += 1,
            (false, false) => cm.tn += 1,
        }
    }
    cm
}

fn compute_metrics(cm: ConfusionMatrix) -> (f64, f64, f64, f64) {
    let total = (cm.tp + cm.tn + cm.fp + cm.fn_val) as f64;
    let accuracy = if total > 0.0 {
        (cm.tp + cm.tn) as f64 / total
    } else {
        0.0
    };
    let precision = if cm.tp + cm.fp > 0 {
        cm.tp as f64 / (cm.tp + cm.fp) as f64
    } else {
        0.0
    };
    let recall = if cm.tp + cm.fn_val > 0 {
        cm.tp as f64 / (cm.tp + cm.fn_val) as f64
    } else {
        0.0
    };
    let f1 = if precision + recall > 0.0 {
        2.0 * precision * recall / (precision + recall)
    } else {
        0.0
    };
    (accuracy, precision, recall, f1)
}

/// Splitting data (stratified)
pub fn train_test_split(
    features: &[Vec<f64>],
    labels: &[bool],
    train_ratio: f64,
    rng: &mut StdRng,
) -> (Vec<Vec<f64>>, Vec<bool>, Vec<Vec<f64>>, Vec<bool>) {
    let mut class0 = Vec::new();
    let mut class1 = Vec::new();
    for (i, &l) in labels.iter().enumerate() {
        if l {
            class1.push(i);
        } else {
            class0.push(i);
        }
    }

    class0.shuffle(rng);
    class1.shuffle(rng);

    let n_train0 = (class0.len() as f64 * train_ratio).round() as usize;
    let n_train1 = (class1.len() as f64 * train_ratio).round() as usize;

    let mut train_features = Vec::new();
    let mut train_labels = Vec::new();
    let mut test_features = Vec::new();
    let mut test_labels = Vec::new();

    for &i in class0.iter().take(n_train0) {
        train_features.push(features[i].clone());
        train_labels.push(false);
    }
    for &i in class1.iter().take(n_train1) {
        train_features.push(features[i].clone());
        train_labels.push(true);
    }
    for &i in class0.iter().skip(n_train0) {
        test_features.push(features[i].clone());
        test_labels.push(false);
    }
    for &i in class1.iter().skip(n_train1) {
        test_features.push(features[i].clone());
        test_labels.push(true);
    }

    // Shuffle train again so batches aren't fully separated by class
    let mut train_indices: Vec<usize> = (0..train_features.len()).collect();
    train_indices.shuffle(rng);
    let train_features_shuf = train_indices
        .iter()
        .map(|&i| train_features[i].clone())
        .collect();
    let train_labels_shuf = train_indices.iter().map(|&i| train_labels[i]).collect();

    (
        train_features_shuf,
        train_labels_shuf,
        test_features,
        test_labels,
    )
}

fn standardise(features: &mut [Vec<f64>], means: &[f64], stds: &[f64]) {
    for row in features.iter_mut() {
        for (j, val) in row.iter_mut().enumerate() {
            if stds[j] > 1e-9 {
                *val = (*val - means[j]) / stds[j];
            } else {
                *val = 0.0;
            }
        }
    }
}

pub struct LogisticRegression {
    weights: Vec<f64>,
    bias: f64,
    means: Vec<f64>,
    stds: Vec<f64>,
}

impl LogisticRegression {
    pub fn fit(train_features: &[Vec<f64>], train_labels: &[bool]) -> Self {
        let n_samples = train_features.len();
        if n_samples == 0 {
            return Self {
                weights: vec![],
                bias: 0.0,
                means: vec![],
                stds: vec![],
            };
        }
        let n_features = train_features[0].len();

        // 1. Compute mean and std
        let mut means = vec![0.0; n_features];
        for row in train_features {
            for j in 0..n_features {
                means[j] += row[j];
            }
        }
        for j in 0..n_features {
            means[j] /= n_samples as f64;
        }

        let mut stds = vec![0.0; n_features];
        for row in train_features {
            for j in 0..n_features {
                let diff = row[j] - means[j];
                stds[j] += diff * diff;
            }
        }
        for j in 0..n_features {
            stds[j] = (stds[j] / n_samples as f64).sqrt();
        }

        // 2. Standardise training data
        let mut standardised_train = train_features.to_vec();
        standardise(&mut standardised_train, &means, &stds);

        // 3. Gradient Descent
        let mut weights = vec![0.0; n_features];
        let mut bias = 0.0;
        let lr = 0.1;
        let lambda = 0.01;
        let iterations = 500;

        for _ in 0..iterations {
            let mut dw = vec![0.0; n_features];
            let mut db = 0.0;

            for (i, row) in standardised_train.iter().enumerate() {
                let y = if train_labels[i] { 1.0 } else { 0.0 };

                let mut z = bias;
                for j in 0..n_features {
                    z += weights[j] * row[j];
                }

                let a = 1.0 / (1.0 + (-z).exp());
                let dz = a - y;

                for j in 0..n_features {
                    dw[j] += dz * row[j];
                }
                db += dz;
            }

            for j in 0..n_features {
                dw[j] /= n_samples as f64;
                dw[j] += (lambda / n_samples as f64) * weights[j]; // L2
                weights[j] -= lr * dw[j];
            }
            db /= n_samples as f64;
            bias -= lr * db;
        }

        Self {
            weights,
            bias,
            means,
            stds,
        }
    }

    pub fn predict_proba(&self, features: &[f64]) -> f64 {
        let mut z = self.bias;
        for j in 0..self.weights.len() {
            let val = if self.stds[j] > 1e-9 {
                (features[j] - self.means[j]) / self.stds[j]
            } else {
                0.0
            };
            z += self.weights[j] * val;
        }
        1.0 / (1.0 + (-z).exp())
    }

    pub fn predict(&self, features: &[f64], threshold: f64) -> bool {
        self.predict_proba(features) >= threshold
    }
}

pub struct GaussianNaiveBayes {
    // [class][feature]
    means: Vec<Vec<f64>>,
    vars: Vec<Vec<f64>>,
    class_priors: Vec<f64>,
}

impl GaussianNaiveBayes {
    pub fn fit(train_features: &[Vec<f64>], train_labels: &[bool]) -> Self {
        let n_samples = train_features.len();
        if n_samples == 0 {
            return Self {
                means: vec![],
                vars: vec![],
                class_priors: vec![],
            };
        }
        let n_features = train_features[0].len();

        let mut counts = [0, 0];
        for &l in train_labels {
            counts[if l { 1 } else { 0 }] += 1;
        }

        let mut means = vec![vec![0.0; n_features]; 2];
        for (i, row) in train_features.iter().enumerate() {
            let c = if train_labels[i] { 1 } else { 0 };
            for j in 0..n_features {
                means[c][j] += row[j];
            }
        }

        for c in 0..2 {
            if counts[c] > 0 {
                for j in 0..n_features {
                    means[c][j] /= counts[c] as f64;
                }
            }
        }

        let mut vars = vec![vec![0.0; n_features]; 2];
        for (i, row) in train_features.iter().enumerate() {
            let c = if train_labels[i] { 1 } else { 0 };
            for j in 0..n_features {
                let diff = row[j] - means[c][j];
                vars[c][j] += diff * diff;
            }
        }

        for c in 0..2 {
            if counts[c] > 1 {
                for j in 0..n_features {
                    vars[c][j] /= (counts[c] - 1) as f64;
                    // Add small epsilon for variance to prevent log(0)
                    vars[c][j] += 1e-9;
                }
            } else {
                for j in 0..n_features {
                    vars[c][j] = 1e-9;
                }
            }
        }

        let class_priors = vec![
            counts[0] as f64 / n_samples as f64,
            counts[1] as f64 / n_samples as f64,
        ];

        Self {
            means,
            vars,
            class_priors,
        }
    }

    pub fn predict_log_proba(&self, features: &[f64]) -> [f64; 2] {
        let mut log_probs = [0.0; 2];
        for c in 0..2 {
            let mut lp = self.class_priors[c].ln();
            for j in 0..features.len() {
                let mean = self.means[c][j];
                let var = self.vars[c][j];
                let diff = features[j] - mean;
                lp += -0.5 * (2.0 * PI * var).ln() - (diff * diff) / (2.0 * var);
            }
            log_probs[c] = lp;
        }
        log_probs
    }

    pub fn predict_proba(&self, features: &[f64]) -> f64 {
        let log_probs = self.predict_log_proba(features);
        // exp(log_p1) / (exp(log_p0) + exp(log_p1))
        // To prevent overflow: p1 = 1 / (1 + exp(log_p0 - log_p1))
        1.0 / (1.0 + (log_probs[0] - log_probs[1]).exp())
    }

    pub fn predict(&self, features: &[f64], threshold: f64) -> bool {
        self.predict_proba(features) >= threshold
    }
}

pub fn evaluate_classifier<F>(
    test_features: &[Vec<f64>],
    test_labels: &[bool],
    predict_proba_fn: F,
) -> (Metrics, ConfusionMatrix, Vec<Point>)
where
    F: Fn(&[f64]) -> f64,
{
    let mut probas = Vec::with_capacity(test_features.len());
    for row in test_features {
        probas.push(predict_proba_fn(row));
    }

    // Default threshold 0.5 for CM and scalar metrics
    let predictions: Vec<bool> = probas.iter().map(|&p| p >= 0.5).collect();
    let cm = compute_cm(&predictions, test_labels);
    let (accuracy, precision, recall, f1) = compute_metrics(cm);

    // Compute ROC and DET curves (200 steps)
    let mut curve_points = Vec::with_capacity(200);
    let steps = 200;
    for i in 0..=steps {
        let t = i as f64 / steps as f64;
        let p_t: Vec<bool> = probas.iter().map(|&p| p >= t).collect();
        let cm_t = compute_cm(&p_t, test_labels);

        let tp = cm_t.tp as f64;
        let tn = cm_t.tn as f64;
        let fp = cm_t.fp as f64;
        let fn_val = cm_t.fn_val as f64;

        let tpr = if tp + fn_val > 0.0 {
            tp / (tp + fn_val)
        } else {
            0.0
        };
        let fpr = if fp + tn > 0.0 { fp / (fp + tn) } else { 0.0 };

        let far = fpr; // False Accept Rate is FPR
        let frr = if tp + fn_val > 0.0 {
            fn_val / (tp + fn_val)
        } else {
            0.0
        }; // False Reject Rate is FNR

        curve_points.push(Point {
            threshold: t,
            far,
            frr,
            tpr,
            fpr,
        });
    }

    // Compute AUC using trapezoidal rule (sort points by FPR ascending)
    // Actually we swept threshold from 0 to 1, so FPR goes from 1 to 0.
    // We can reverse the iteration to go FPR from 0 to 1.
    let mut auc = 0.0;
    for i in 1..curve_points.len() {
        // As threshold increases, FPR decreases. So pt[i].fpr < pt[i-1].fpr.
        // Area = width * avg_height
        let width = curve_points[i - 1].fpr - curve_points[i].fpr;
        let avg_height = (curve_points[i - 1].tpr + curve_points[i].tpr) / 2.0;
        auc += width * avg_height;
    }

    let metrics = Metrics {
        accuracy,
        precision,
        recall,
        f1,
        auc,
    };
    (metrics, cm, curve_points)
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;

    #[test]
    fn test_classifier_better_than_chance() {
        let mut rng = StdRng::seed_from_u64(42);
        // Simple synthetic dataset that is separable
        let mut features = Vec::new();
        let mut labels = Vec::new();
        for _ in 0..100 {
            features.push(vec![1.0, 1.0]);
            labels.push(true);
            features.push(vec![-1.0, -1.0]);
            labels.push(false);
        }

        let (tr_f, tr_l, te_f, te_l) = train_test_split(&features, &labels, 0.7, &mut rng);

        let lr = LogisticRegression::fit(&tr_f, &tr_l);
        let gnb = GaussianNaiveBayes::fit(&tr_f, &tr_l);

        let (metrics_lr, _, _) = evaluate_classifier(&te_f, &te_l, |f| lr.predict_proba(f));
        let (metrics_gnb, _, _) = evaluate_classifier(&te_f, &te_l, |f| gnb.predict_proba(f));

        assert!(metrics_lr.accuracy > 0.55);
        assert!(metrics_gnb.accuracy > 0.55);
    }
}
