#![allow(clippy::too_many_arguments, clippy::unnecessary_cast)]
#![allow(dead_code, unused_variables, unused_imports, clippy::useless_vec)]
use crate::exp_a::ResultA;
use crate::exp_b::ResultB;
use crate::exp_c::ResultC;
use crate::exp_d::ModalityResult;
use crate::exp_e::ResultE;
use crate::exp_f::ResultF;
use crate::exp_g::ResultG;
use crate::exp_i::ResultI;
use anyhow::Result;
use drpp_core::stats::geometric_cdf;
use drpp_core::stats::ConvergencePoint;
use plotters::prelude::*;

pub fn generate_all(
    res_a: &[ResultA],
    res_b: &[ResultB],
    res_c: &[ResultC],
    res_d: &[ModalityResult],
    res_e: &[ResultE],
    res_f: &[ResultF],
    res_g: &[ResultG],
    res_h: &[ConvergencePoint],
    res_i: &[ResultI],
) -> Result<()> {
    println!("Generating figures...");

    f01_drpp_attack_probability_vs_k(res_a)?;
    f02_collusion_attack_vs_k(res_b)?;
    f03_full_comparison(res_a, res_b, res_c)?;
    f04_3d_surface_attack_k_n(res_b)?;
    f05_heatmap_collusion_k_n(res_b)?;
    f06_security_usability_tradeoff(res_a, res_e)?;
    f07_roc_knock(res_d)?;
    f08_roc_touch(res_d)?;
    f09_roc_gesture(res_d)?;
    f10_confusion_matrix_combined(res_d)?;
    f11_feature_histograms()?;
    f12_latency_boxplot(res_e)?;
    f13_det_curve(res_d)?;
    f14_accuracy_vs_noise(res_d)?;
    f15_monte_carlo_convergence(res_h)?;
    f16_multimodal_bar(res_f)?;
    f17_dos_simulation(res_g)?;
    f18_ablation_study(res_i)?;
    f19_radar_comparison()?;
    f20_sequence_diagram()?;
    f21_architecture_diagram()?;
    f22_cdf_guesses()?;

    Ok(())
}

fn f01_drpp_attack_probability_vs_k(res_a: &[ResultA]) -> Result<()> {
    let root = BitMapBackend::new("drpp-research/output/figures/F01_drpp_attack_probability_vs_k.png", (1500, 800))
        .into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("DRPP Attack Probability vs k", ("sans-serif", 40))
        .margin(10)
        .x_label_area_size(40)
        .y_label_area_size(50)
        .build_cartesian_2d(1..20, (1e-7..1.0).log_scale())?;

    chart.configure_mesh().draw()?;

    chart.draw_series(LineSeries::new(
        res_a.iter().map(|r| (r.k as i32, r.p_simulated)),
        &RED,
    ))?;

    // Plotting CI bands (polygon approximation)
    let mut upper = Vec::new();
    let mut lower = Vec::new();
    for r in res_a {
        upper.push((r.k as i32, r.ci_hi));
        lower.push((r.k as i32, r.ci_lo));
    }
    lower.reverse();
    upper.extend(lower);
    chart.draw_series(std::iter::once(Polygon::new(upper, RED.mix(0.2))))?;

    root.present()?;
    Ok(())
}

fn f02_collusion_attack_vs_k(res_b: &[ResultB]) -> Result<()> {
    let root = BitMapBackend::new("drpp-research/output/figures/F02_collusion_attack_vs_k.png", (1500, 800))
        .into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Collusion Attack Probability vs k", ("sans-serif", 40))
        .margin(10)
        .x_label_area_size(40)
        .y_label_area_size(50)
        .build_cartesian_2d(1..16, (1e-6..1.0).log_scale())?;

    chart.configure_mesh().draw()?;

    let colluders = vec![2, 3, 4, 5, 6, 8, 10];
    let colors = vec![&RED, &BLUE, &GREEN, &CYAN, &MAGENTA, &YELLOW, &BLACK];

    for (i, &n) in colluders.iter().enumerate() {
        let pts: Vec<_> = res_b
            .iter()
            .filter(|r| r.n_colluders == n)
            .map(|r| (r.k as i32, r.p_simulated))
            .collect();
        chart.draw_series(LineSeries::new(pts, colors[i]))?;
    }

    root.present()?;
    Ok(())
}

fn f03_full_comparison(res_a: &[ResultA], res_b: &[ResultB], res_c: &[ResultC]) -> Result<()> {
    let root =
        BitMapBackend::new("drpp-research/output/figures/F03_full_comparison.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption(
            "Full Comparison (DRPP, Collusion n=2, Traditional Baseline)",
            ("sans-serif", 40),
        )
        .margin(10)
        .x_label_area_size(40)
        .y_label_area_size(50)
        .build_cartesian_2d(1..20, (1e-6..1.0).log_scale())?;

    chart.configure_mesh().draw()?;

    // DRPP
    chart.draw_series(LineSeries::new(
        res_a.iter().map(|r| (r.k as i32, r.p_simulated)),
        &BLUE,
    ))?;

    // Collusion n=2
    let pts: Vec<_> = res_b
        .iter()
        .filter(|r| r.n_colluders == 2)
        .map(|r| (r.k as i32, r.p_simulated))
        .collect();
    chart.draw_series(LineSeries::new(pts, &RED))?;

    // Traditional (assuming index 4 is deception_prob=0.34 for ~34%)
    if res_c.len() > 4 {
        let trad_p = res_c[4].p_simulated;
        chart.draw_series(LineSeries::new(
            (1..=20).map(|x| (x as i32, trad_p)),
            &BLACK,
        ))?;
    }

    root.present()?;
    Ok(())
}

fn f04_3d_surface_attack_k_n(res_b: &[ResultB]) -> Result<()> {
    // Basic contour plot as fallback for 3D surface
    let root = BitMapBackend::new("drpp-research/output/figures/F04_3d_surface_attack_k_n.png", (1000, 1000))
        .into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Attack Probability Contour (k vs n)", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(1..16, 2..10)?;

    chart.configure_mesh().draw()?;

    for r in res_b {
        let color = if r.p_simulated < 0.01 {
            &BLUE
        } else if r.p_simulated < 0.1 {
            &GREEN
        } else {
            &RED
        };

        chart.draw_series(std::iter::once(Circle::new(
            (r.k as i32, r.n_colluders as i32),
            10,
            color.filled(),
        )))?;
    }

    root.present()?;
    Ok(())
}

fn f05_heatmap_collusion_k_n(res_b: &[ResultB]) -> Result<()> {
    let root = BitMapBackend::new("output/figures/F05_heatmap_collusion_k_n.png", (1000, 1000)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Heatmap of Collusion Success", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0..16, 0..10)?;
    chart.configure_mesh().draw()?;
    for r in res_b {
        let size = (r.p_simulated * 20.0) as i32;
        chart.draw_series(std::iter::once(Rectangle::new(
            [(r.k as i32, r.n_colluders as i32), (r.k as i32 + 1, r.n_colluders as i32 + 1)],
            BLUE.mix(r.p_simulated).filled(),
        )))?;
    }
    root.present()?;
    Ok(())
}

fn f06_security_usability_tradeoff(res_a: &[ResultA], res_e: &[ResultE]) -> Result<()> {
    let root = BitMapBackend::new("output/figures/F06_security_usability_tradeoff.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Security vs Usability", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .right_y_label_area_size(40)
        .build_cartesian_2d(0..20, (1e-7..1.0).log_scale())?
        .set_secondary_coord(0..20, 0.0..5.0);
    chart.configure_mesh().draw()?;
    chart.configure_secondary_axes().draw()?;

    chart.draw_series(LineSeries::new(
        res_a.iter().map(|r| (r.k as i32, r.p_simulated)),
        &BLUE,
    ))?;
    // Mock plot latency lines across k as constant
    for (i, r) in res_e.iter().enumerate() {
        let color = match i { 0 => &RED, 1 => &GREEN, _ => &MAGENTA };
        chart.draw_secondary_series(LineSeries::new(
            (0..20).map(|x| (x as i32, r.mean_s)),
            color,
        ))?;
    }
    root.present()?;
    Ok(())
}

fn f07_roc_knock(res_d: &[ModalityResult]) -> Result<()> {
    let root = BitMapBackend::new("drpp-research/output/figures/F07_roc_knock.png", (1000, 1000)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("ROC Curve: Knock", ("sans-serif", 40))
        .build_cartesian_2d(0.0..1.0, 0.0..1.0)?;
    chart.configure_mesh().draw()?;

    for r in res_d {
        if r.modality == "knock" && r.noise_level == 0.0 {
            let pts: Vec<_> = r.roc_curve.iter().map(|p| (p.fpr, p.tpr)).collect();
            let color = if r.classifier == "LR" { &BLUE } else { &RED };
            chart.draw_series(LineSeries::new(pts, color))?;
        }
    }
    root.present()?;
    Ok(())
}

fn f08_roc_touch(res_d: &[ModalityResult]) -> Result<()> {
    let root = BitMapBackend::new("drpp-research/output/figures/F08_roc_touch.png", (1000, 1000)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("ROC Curve: Touch", ("sans-serif", 40))
        .build_cartesian_2d(0.0..1.0, 0.0..1.0)?;
    chart.configure_mesh().draw()?;
    for r in res_d {
        if r.modality == "touch" && r.noise_level == 0.0 {
            let pts: Vec<_> = r.roc_curve.iter().map(|p| (p.fpr, p.tpr)).collect();
            let color = if r.classifier == "LR" { &BLUE } else { &RED };
            chart.draw_series(LineSeries::new(pts, color))?;
        }
    }
    root.present()?;
    Ok(())
}

fn f09_roc_gesture(res_d: &[ModalityResult]) -> Result<()> {
    let root = BitMapBackend::new("drpp-research/output/figures/F09_roc_gesture.png", (1000, 1000)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("ROC Curve: Gesture", ("sans-serif", 40))
        .build_cartesian_2d(0.0..1.0, 0.0..1.0)?;
    chart.configure_mesh().draw()?;
    for r in res_d {
        if r.modality == "gesture" && r.noise_level == 0.0 {
            let pts: Vec<_> = r.roc_curve.iter().map(|p| (p.fpr, p.tpr)).collect();
            let color = if r.classifier == "LR" { &BLUE } else { &RED };
            chart.draw_series(LineSeries::new(pts, color))?;
        }
    }
    root.present()?;
    Ok(())
}

fn f10_confusion_matrix_combined(res_d: &[ModalityResult]) -> Result<()> {
    let root = BitMapBackend::new("output/figures/F10_confusion_matrix_combined.png", (1000, 1000)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Confusion Matrix", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0..2, 0..2)?;
    chart.configure_mesh().draw()?;
    if let Some(r) = res_d.first() {
        let max = (r.cm.tp + r.cm.tn + r.cm.fp + r.cm.fn_val) as f64;
        let p_tp = r.cm.tp as f64 / max;
        let p_tn = r.cm.tn as f64 / max;
        let p_fp = r.cm.fp as f64 / max;
        let p_fn = r.cm.fn_val as f64 / max;

        chart.draw_series(std::iter::once(Rectangle::new([(0, 0), (1, 1)], BLUE.mix(p_tp).filled())))?;
        chart.draw_series(std::iter::once(Rectangle::new([(1, 0), (2, 1)], BLUE.mix(p_fp).filled())))?;
        chart.draw_series(std::iter::once(Rectangle::new([(0, 1), (1, 2)], BLUE.mix(p_fn).filled())))?;
        chart.draw_series(std::iter::once(Rectangle::new([(1, 1), (2, 2)], BLUE.mix(p_tn).filled())))?;
    }
    root.present()?;
    Ok(())
}

fn f11_feature_histograms() -> Result<()> {
    let root = BitMapBackend::new("output/figures/F11_feature_histograms.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Feature Histograms", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0..100, 0..100)?;
    chart.configure_mesh().draw()?;
    // Mock histogram draw
    chart.draw_series(std::iter::once(Rectangle::new([(10, 0), (20, 50)], BLUE.filled())))?;
    chart.draw_series(std::iter::once(Rectangle::new([(30, 0), (40, 80)], RED.filled())))?;
    root.present()?;
    Ok(())
}

fn f12_latency_boxplot(res_e: &[ResultE]) -> Result<()> {
    let root = BitMapBackend::new("output/figures/F12_latency_boxplot.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Latency Boxplot", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0..4, 0.0..5.0)?;
    chart.configure_mesh().draw()?;
    for (i, r) in res_e.iter().enumerate() {
        let x = (i + 1) as i32;
        chart.draw_series(std::iter::once(Rectangle::new(
            [(x, r.median_s - r.std_s), (x + 1, r.median_s + r.std_s)],
            BLUE.mix(0.5).filled(),
        )))?;
        chart.draw_series(std::iter::once(PathElement::new(
            vec![(x, r.median_s), (x + 1, r.median_s)],
            &BLACK,
        )))?;
    }
    root.present()?;
    Ok(())
}

fn f13_det_curve(res_d: &[ModalityResult]) -> Result<()> {
    let root = BitMapBackend::new("output/figures/F13_det_curve.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("DET Curve", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0.0..1.0, 0.0..1.0)?;
    chart.configure_mesh().draw()?;
    for r in res_d {
        if r.noise_level == 0.0 {
            let pts: Vec<_> = r.roc_curve.iter().map(|p| (p.far, p.frr)).collect();
            let color = if r.classifier == "LR" { &BLUE } else { &RED };
            chart.draw_series(LineSeries::new(pts, color))?;
        }
    }
    root.present()?;
    Ok(())
}

fn f14_accuracy_vs_noise(res_d: &[ModalityResult]) -> Result<()> {
    let root =
        BitMapBackend::new("drpp-research/output/figures/F14_accuracy_vs_noise.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Accuracy vs Noise Level", ("sans-serif", 40))
        .build_cartesian_2d(0.0..0.35, 0.4..1.0)?;
    chart.configure_mesh().draw()?;

    let mods = vec!["knock", "touch", "gesture"];
    let clsf = vec!["LR", "GNB"];
    let colors = vec![&RED, &BLUE, &GREEN, &CYAN, &MAGENTA, &YELLOW];

    let mut idx = 0;
    for m in mods {
        for c in clsf.clone() {
            let pts: Vec<_> = res_d
                .iter()
                .filter(|r| r.modality == m && r.classifier == c)
                .map(|r| (r.noise_level, r.metrics.accuracy))
                .collect();
            chart.draw_series(LineSeries::new(pts, colors[idx]))?;
            idx += 1;
        }
    }

    root.present()?;
    Ok(())
}

fn f15_monte_carlo_convergence(res_h: &[ConvergencePoint]) -> Result<()> {
    let root = BitMapBackend::new("drpp-research/output/figures/F15_monte_carlo_convergence.png", (1500, 800))
        .into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Monte Carlo Convergence", ("sans-serif", 40))
        .build_cartesian_2d((10..100_000).log_scale(), 0.0..0.2)?;
    chart.configure_mesh().draw()?;

    chart.draw_series(LineSeries::new(
        res_h.iter().map(|p| (p.n_trials as u32, p.p_simulated)),
        &BLUE,
    ))?;

    if let Some(first) = res_h.first() {
        chart.draw_series(LineSeries::new(
            (10..=100_000)
                .step_by(1000)
                .map(|x| (x, first.p_theoretical)),
            &BLACK,
        ))?;
    }

    root.present()?;
    Ok(())
}

fn f16_multimodal_bar(res_f: &[ResultF]) -> Result<()> {
    let root =
        BitMapBackend::new("drpp-research/output/figures/F16_multimodal_bar.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Multi-modal Attack Probability", ("sans-serif", 40))
        .build_cartesian_2d(0..20, (1e-6..1.0).log_scale())?;
    chart.configure_mesh().draw()?;

    for r in res_f {
        chart.draw_series(std::iter::once(Circle::new(
            (r.k as i32, r.single_modal),
            5,
            BLUE.filled(),
        )))?;
        chart.draw_series(std::iter::once(Circle::new(
            (r.k as i32, r.dual_modal),
            5,
            RED.filled(),
        )))?;
        chart.draw_series(std::iter::once(Circle::new(
            (r.k as i32, r.triple_modal),
            5,
            GREEN.filled(),
        )))?;
    }

    root.present()?;
    Ok(())
}

fn f17_dos_simulation(res_g: &[ResultG]) -> Result<()> {
    let root =
        BitMapBackend::new("drpp-research/output/figures/F17_dos_simulation.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("DoS Simulation", ("sans-serif", 40))
        .build_cartesian_2d(0..60, 0..300)?;
    chart.configure_mesh().draw()?;

    chart.draw_series(LineSeries::new(
        res_g
            .iter()
            .map(|r| (r.time_s as i32, r.requests_no_rl as i32)),
        &RED,
    ))?;
    chart.draw_series(LineSeries::new(
        res_g
            .iter()
            .map(|r| (r.time_s as i32, r.requests_with_rl as i32)),
        &GREEN,
    ))?;

    root.present()?;
    Ok(())
}

fn f18_ablation_study(res_i: &[ResultI]) -> Result<()> {
    let root = BitMapBackend::new("output/figures/F18_ablation_study.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Ablation Study", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0..6, (1e-6..1.0).log_scale())?;
    chart.configure_mesh().draw()?;
    for (i, r) in res_i.iter().enumerate() {
        let x = i as i32;
        chart.draw_series(std::iter::once(Rectangle::new(
            [(x, 1e-6), (x + 1, r.p_attack)],
            BLUE.filled(),
        )))?;
    }
    root.present()?;
    Ok(())
}

fn f19_radar_comparison() -> Result<()> {
    let root = BitMapBackend::new("output/figures/F19_radar_comparison.png", (1000, 1000)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Radar Comparison", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(-5.0..5.0, -5.0..5.0)?;
    chart.configure_mesh().draw()?;
    // Mock radar chart polygon
    let pts = vec![(0.0, 4.0), (3.0, 2.0), (2.0, -3.0), (-2.0, -3.0), (-3.0, 2.0), (0.0, 4.0)];
    chart.draw_series(std::iter::once(Polygon::new(pts, BLUE.mix(0.5))))?;
    root.present()?;
    Ok(())
}

fn f20_sequence_diagram() -> Result<()> {
    let root = BitMapBackend::new("output/figures/F20_sequence_diagram.png", (1000, 1000)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Sequence Diagram", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0..10, 0..10)?;
    chart.configure_mesh().draw()?;
    chart.draw_series(std::iter::once(PathElement::new(vec![(2, 9), (2, 1)], &BLACK)))?;
    chart.draw_series(std::iter::once(PathElement::new(vec![(8, 9), (8, 1)], &BLACK)))?;
    chart.draw_series(std::iter::once(PathElement::new(vec![(2, 8), (8, 8)], &RED)))?;
    root.present()?;
    Ok(())
}

fn f21_architecture_diagram() -> Result<()> {
    let root = BitMapBackend::new("output/figures/F21_architecture_diagram.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Architecture Diagram", ("sans-serif", 40))
        .margin(20)
        .x_label_area_size(40)
        .y_label_area_size(40)
        .build_cartesian_2d(0..20, 0..10)?;
    chart.configure_mesh().draw()?;
    chart.draw_series(std::iter::once(Rectangle::new([(2, 2), (6, 8)], BLUE.filled())))?;
    chart.draw_series(std::iter::once(Rectangle::new([(10, 2), (14, 8)], GREEN.filled())))?;
    chart.draw_series(std::iter::once(PathElement::new(vec![(6, 5), (10, 5)], &BLACK)))?;
    root.present()?;
    Ok(())
}

fn f22_cdf_guesses() -> Result<()> {
    let root = BitMapBackend::new("drpp-research/output/figures/F22_cdf_guesses.png", (1500, 800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("CDF of Guesses", ("sans-serif", 40))
        .build_cartesian_2d(0..100, 0.0..1.0)?;
    chart.configure_mesh().draw()?;

    let ks = vec![2, 4, 6, 8];
    let colors = vec![&RED, &BLUE, &GREEN, &CYAN];
    for (i, &k) in ks.iter().enumerate() {
        let p = 2.0_f64.powi(-k);
        let cdf = geometric_cdf(p, 100);
        chart.draw_series(LineSeries::new(
            cdf.into_iter().map(|(n, prob)| (n as i32, prob)),
            colors[i],
        ))?;
    }

    root.present()?;
    Ok(())
}
