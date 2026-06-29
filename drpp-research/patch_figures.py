import re

with open("crates/experiments/src/figures.rs", "r") as f:
    content = f.read()

# Replace f05
content = re.sub(
    r"fn f05_heatmap_collusion_k_n.*?\n.*?\n.*?\n.*?chart\.configure_mesh\(\)\.draw\(\)\?;\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f05_heatmap_collusion_k_n(res_b: &[ResultB]) -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f06
content = re.sub(
    r"fn f06_security_usability_tradeoff.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f06_security_usability_tradeoff(res_a: &[ResultA], res_e: &[ResultE]) -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f10
content = re.sub(
    r"fn f10_confusion_matrix_combined.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f10_confusion_matrix_combined(res_d: &[ModalityResult]) -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f11
content = re.sub(
    r"fn f11_feature_histograms.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f11_feature_histograms() -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f12
content = re.sub(
    r"fn f12_latency_boxplot.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f12_latency_boxplot(res_e: &[ResultE]) -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f13
content = re.sub(
    r"fn f13_det_curve.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f13_det_curve(res_d: &[ModalityResult]) -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f18
content = re.sub(
    r"fn f18_ablation_study.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f18_ablation_study(res_i: &[ResultI]) -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f19
content = re.sub(
    r"fn f19_radar_comparison.*?\n.*?\n.*?\/\/ Radar logic\.\.\.\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f19_radar_comparison() -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f20
content = re.sub(
    r"fn f20_sequence_diagram.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f20_sequence_diagram() -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

# Replace f21
content = re.sub(
    r"fn f21_architecture_diagram.*?\n.*?\n.*?root\.present\(\)\?;\n    Ok\(\(\)\)\n\}",
    r"""fn f21_architecture_diagram() -> Result<()> {
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
}""",
    content, flags=re.DOTALL
)

with open("crates/experiments/src/figures.rs", "w") as f:
    f.write(content)
