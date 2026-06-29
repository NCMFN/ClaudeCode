with open("crates/experiments/src/main.rs", "r") as f:
    lines = f.readlines()

with open("crates/experiments/src/main.rs", "w") as f:
    for line in lines:
        if "fn print_download_manifest() -> Result<()> {" in line:
            f.write("fn print_download_manifest() -> Result<()> {\n")
            f.write("    println!(\"✅ Figures written to drpp-research/output/figures/\");\n")
            f.write("    let figures_dir = Path::new(\"output/figures\");\n")
        elif "let figures_dir = Path::new(\"drpp-research/output/figures\");" in line:
            continue
        elif "println!(\"✅ Figures written to drpp-research/output/figures/\");" in line:
            continue
        else:
            f.write(line)
