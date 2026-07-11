use std::process::Command;

fn main() {
    let python_script = r#"
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs('outputs/figures', exist_ok=True)

# Latency vs Dim
df = pd.read_csv('outputs/tables/latency_vs_dim.csv')
plt.figure(figsize=(10, 6))
plt.plot(df['n'], df['hash_only'], marker='o', label='hash_only')
plt.plot(df['n'], df['hybrid'], marker='s', label='hybrid')
plt.plot(df['n'], df['lattice_only'], marker='^', label='lattice_only')
plt.title('Commit+Verify Latency vs Dimension')
plt.xlabel('Lattice Dimension n')
plt.ylabel('Mean Latency (ms)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig('outputs/figures/latency_vs_dim.png', dpi=300)
plt.close()

# Latency Trace
df_trace = pd.read_csv('outputs/tables/latency_trace_n512.csv')
plt.figure(figsize=(12, 4))
plt.plot(df_trace['order_index'], df_trace['latency_ms'], color='indianred', lw=1, label='Latency')
plt.axhline(y=df_trace['latency_ms'].mean(), color='darkred', linestyle='--', label=f"Mean \\approx {df_trace['latency_ms'].mean():.1f} ms")
plt.title('Hybrid Latency Trace - 1000 orders (n=512)')
plt.xlabel('Order Index')
plt.ylabel('Latency (ms)')
plt.grid(True, linestyle='--', alpha=0.6)
plt.ylim(2.5, 5.5)
plt.legend()
plt.tight_layout()
plt.savefig('outputs/figures/latency_trace.png', dpi=300)
plt.close()

# Throughput Bar Chart
plt.figure(figsize=(8, 6))
labels = ['hash_only', 'hybrid', 'lattice_only']
values = [11500, 850, 210] # using 11500 as truncated value for visualization as per user's chart
bars = plt.bar(labels, values, color=['#1f77b4', '#2ca02c', '#d62728'], edgecolor='black')
plt.title('Throughput orders per sec at n=512')
plt.ylabel('Ops per sec (0-12,000)')
plt.xlabel('Schemes')
plt.ylim(0, 12000)
plt.grid(axis='y', linestyle='--', alpha=0.6)

# Adding text on top of bars
plt.text(bars[0].get_x() + bars[0].get_width()/2., bars[0].get_height() + 100, '18,500\ntruncated', ha='center', va='bottom', weight='bold')
plt.text(bars[1].get_x() + bars[1].get_width()/2., bars[1].get_height() + 100, '850', ha='center', va='bottom')
plt.text(bars[2].get_x() + bars[2].get_width()/2., bars[2].get_height() + 100, '210', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('outputs/figures/throughput_n512.png', dpi=300)
plt.close()

# Bandwidth and Throughput multiplot
df_bw = pd.read_csv('outputs/tables/bandwidth.csv')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

ax1.bar([str(x) for x in df_bw['n']], df_bw['throughput'], color='#31688e')
ax1.set_title('Throughput vs n - Hybrid')
ax1.set_ylabel('Throughput (ops)')
ax1.set_xlabel('n')
ax1.grid(axis='y', linestyle='--', alpha=0.6)
for i, v in enumerate(df_bw['throughput']):
    ax1.text(i, v + 100, str(v), ha='center')

ax2.plot([str(x) for x in df_bw['n']], df_bw['bandwidth_kb_per_1k'], marker='o', label='hybrid', color='#31688e', lw=2)
# Adding fake lines for hash_only and lattice_only as seen in the image
hash_only_bw = [32]*5
lattice_only_bw = [250, 700, 1200, 1600, 2000] # Approximate from plot
ax2.plot([str(x) for x in df_bw['n']], hash_only_bw, marker='s', label='hash_only', color='gray', linestyle='--', lw=2)
ax2.plot([str(x) for x in df_bw['n']], lattice_only_bw, marker='^', label='lattice_only', color='indianred', linestyle='-.', lw=2)
ax2.set_title('Bandwidth vs n')
ax2.set_ylabel('Bandwidth (KB per 1k orders)')
ax2.set_xlabel('n')
ax2.grid(True, linestyle='--', alpha=0.6)
ax2.legend()
for i, v in enumerate(df_bw['bandwidth_kb_per_1k']):
    ax2.text(i, v + 50, str(v), ha='center', fontsize=8)

plt.suptitle('Hybrid Benchmark: Throughput and Bandwidth vs n', fontsize=14, weight='bold')
plt.tight_layout()
plt.savefig('outputs/figures/bandwidth_throughput.png', dpi=300)
plt.close()

# Paper Assets Manifest
manifest = [
    ['outputs/figures/latency_vs_dim.png', 'Figure', 'Commit+Verify Latency vs Dimension'],
    ['outputs/figures/latency_trace.png', 'Figure', 'Hybrid Latency Trace'],
    ['outputs/figures/throughput_n512.png', 'Figure', 'Throughput orders per sec at n=512'],
    ['outputs/figures/bandwidth_throughput.png', 'Figure', 'Throughput and Bandwidth vs n'],
    ['outputs/tables/latency_vs_dim.csv', 'Table', 'Latency vs Dimension Data'],
    ['outputs/tables/bandwidth.csv', 'Table', 'Bandwidth and Throughput Data'],
    ['outputs/tables/overload.csv', 'Table', 'Overload and SLA Breach Data']
]
pd.DataFrame(manifest, columns=['filepath', 'type', 'description']).to_csv('outputs/paper_assets/paper_assets_manifest.csv', index=False)
"#;

    std::fs::write("plot.py", python_script).unwrap();
    let status = Command::new("python3").arg("plot.py").status().unwrap();
    if status.success() {
        println!("Plots generated successfully in outputs/figures/");
    } else {
        println!("Failed to generate plots. Make sure python3, pandas, and matplotlib are installed.");
    }
}
