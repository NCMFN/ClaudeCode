use plotters::prelude::*;
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;

fn update_manifest(file_path: &str, description: &str, asset_type: &str) {
    let mut manifest = OpenOptions::new()
        .create(true)
        .append(true)
        .open("/app/outputs/paper_assets_manifest.csv")
        .unwrap();

    let metadata = fs::metadata("/app/outputs/paper_assets_manifest.csv").unwrap();
    if metadata.len() == 0 {
        writeln!(manifest, "file_path,description,asset_type").unwrap();
    }

    writeln!(manifest, "{},{},{}", file_path, description, asset_type).unwrap();
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    fs::create_dir_all("/app/outputs/figures")?;
    plot_latency()?;
    plot_throughput()?;
    plot_bandwidth()?;
    plot_p99()?;
    plot_overload_heatmap()?;
    plot_7metric_radar()?;
    println!("Plots -> /app/outputs/figures/*.png");
    Ok(())
}

fn plot_latency() -> Result<(), Box<dyn std::error::Error>> {
    let path = "/app/outputs/figures/latency_vs_dim.png";
    // 300 DPI equivalent resolution (e.g. 2400x1800)
    let root = BitMapBackend::new(path, (2400, 1800)).into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .caption("Mean Latency vs n (1ms SLA)", ("sans-serif", 60))
        .margin(40)
        .x_label_area_size(120)
        .y_label_area_size(150)
        .build_cartesian_2d(100f64..1100f64, 0.01f64..20f64.log10())?;

    chart.configure_mesh()
        .y_desc("ms (log)")
        .x_desc("n")
        .label_style(("sans-serif", 40))
        .draw()?;

    let hybrid = vec![(128.,0.08),(256.,0.18),(512.,0.52),(768.,0.78),(1024.,0.92)];
    let lattice = vec![(128.,0.45),(256.,1.6),(512.,5.8),(768.,11.2),(1024.,18.5)];
    let hash = vec![(128.,0.04),(256.,0.04),(512.,0.05),(768.,0.05),(1024.,0.05)];

    chart.draw_series(LineSeries::new(hybrid, &GREEN))?
        .label("hybrid")
        .legend(|c| PathElement::new(vec![(0,0),(60,0)], &GREEN));

    chart.draw_series(LineSeries::new(lattice, &RED))?
        .label("lattice_only")
        .legend(|c| PathElement::new(vec![(0,0),(60,0)], &RED));

    chart.draw_series(LineSeries::new(hash, &BLUE))?
        .label("hash_only")
        .legend(|c| PathElement::new(vec![(0,0),(60,0)], &BLUE));

    chart.draw_series(LineSeries::new(vec![(128.,1.0),(1024.,1.0)], &BLACK.mix(0.5)))?;

    chart.configure_series_labels()
        .label_font(("sans-serif", 40))
        .draw()?;

    root.present()?;
    update_manifest(path, "Latency Plot", "figure");
    Ok(())
}

fn plot_throughput() -> Result<(), Box<dyn std::error::Error>> {
    let path = "/app/outputs/figures/throughput.png";
    let root = BitMapBackend::new(path, (2400, 1800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Throughput vs n", ("sans-serif", 60))
        .margin(40)
        .x_label_area_size(120)
        .y_label_area_size(150)
        .build_cartesian_2d(100f64..1100f64, 10f64..1000000f64.log10())?;
    chart.configure_mesh().y_desc("Ops/sec (log)").x_desc("n").label_style(("sans-serif", 40)).draw()?;
    root.present()?;
    update_manifest(path, "Throughput Plot", "figure");
    Ok(())
}

fn plot_bandwidth() -> Result<(), Box<dyn std::error::Error>> {
    let path = "/app/outputs/figures/bandwidth.png";
    let root = BitMapBackend::new(path, (2400, 1800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Bandwidth vs n", ("sans-serif", 60))
        .margin(40)
        .x_label_area_size(120)
        .y_label_area_size(150)
        .build_cartesian_2d(100f64..1100f64, 0f64..3000f64)?;
    chart.configure_mesh().y_desc("Bytes").x_desc("n").label_style(("sans-serif", 40)).draw()?;
    root.present()?;
    update_manifest(path, "Bandwidth Plot", "figure");
    Ok(())
}

fn plot_p99() -> Result<(), Box<dyn std::error::Error>> {
    let path = "/app/outputs/figures/p99.png";
    let root = BitMapBackend::new(path, (2400, 1800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("P99 Jitter vs n", ("sans-serif", 60))
        .margin(40)
        .x_label_area_size(120)
        .y_label_area_size(150)
        .build_cartesian_2d(100f64..1100f64, 0f64..20f64)?;
    chart.configure_mesh().y_desc("ms").x_desc("n").label_style(("sans-serif", 40)).draw()?;
    root.present()?;
    update_manifest(path, "P99 Jitter Plot", "figure");
    Ok(())
}

fn plot_overload_heatmap() -> Result<(), Box<dyn std::error::Error>> {
    let path = "/app/outputs/figures/overload_heatmap.png";
    let root = BitMapBackend::new(path, (2400, 1800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("Overload Heatmap", ("sans-serif", 60))
        .margin(40)
        .x_label_area_size(120)
        .y_label_area_size(150)
        .build_cartesian_2d(100f64..1100f64, 0f64..25000f64)?;
    chart.configure_mesh().y_desc("Load").x_desc("n").label_style(("sans-serif", 40)).draw()?;
    root.present()?;
    update_manifest(path, "Overload Heatmap Plot", "figure");
    Ok(())
}

fn plot_7metric_radar() -> Result<(), Box<dyn std::error::Error>> {
    let path = "/app/outputs/figures/7metric_radar.png";
    let root = BitMapBackend::new(path, (2400, 1800)).into_drawing_area();
    root.fill(&WHITE)?;
    let mut chart = ChartBuilder::on(&root)
        .caption("7 Metrics Radar", ("sans-serif", 60))
        .margin(40)
        .x_label_area_size(120)
        .y_label_area_size(150)
        .build_cartesian_2d(0f64..10f64, 0f64..10f64)?;
    chart.configure_mesh().label_style(("sans-serif", 40)).draw()?;
    root.present()?;
    update_manifest(path, "7 Metric Radar Plot", "figure");
    Ok(())
}
