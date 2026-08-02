# Claude Code Resources 🚀

> A curated collection of the best GitHub repositories to supercharge your Claude Code workflow in 2026.

---

## 📚 Top 12 Repos That Will 10x Your Next Project

| # | Repository | Description |
|---|------------|-------------|
| 1 | [Claude Mem](https://github.com/thedotmack/claude-mem) | Persistent memory across sessions — stop re-teaching Claude your codebase |
| 2 | [UI UX Pro Max](https://github.com/czlonkowski/n8n-mcp) | 50+ styles, 161 color palettes, 99 UX guidelines — Claude stops building ugly UIs |
| 3 | [n8n-MCP](https://github.com/czlonkowski/n8n-mcp) | Connect Claude Code to 400+ n8n integrations via MCP |
| 4 | [LightRAG](https://github.com/hkuds/lightrag) | Graph + vector RAG — lets Claude understand large codebases structurally |
| 5 | [Everything Claude Code](https://github.com/affaan-m/everything-claude-code) | Skills, instincts, security scanning, multi-language coverage — full agent harness |
| 6 | [Awesome Claude Code](https://github.com/sickn33/antigravity) | Community bible — curated skills, hooks, slash commands, orchestrators |
| 7 | [Superpowers](https://github.com/obra/superpowers) | Forces structured thinking before writing a single line of code |
| 8 | [Claude Code Ultimate Guide](https://github.com/FlorianBruniau/claude-code-ultimate-guide) | 23K+ lines of docs, 219 templates, 271 quizzes — beginner to power user |
| 9 | [Antigravity Awesome Skills](https://github.com/sickn33/antigravity) | 1,200+ ready-to-use skills — one of the largest collections |
| 10 | [Claude Agent Blueprints](https://github.com/danielrosehill/claude-agent-blueprints) | 75+ agent workspace templates beyond coding |
| 11 | [VoiceMode MCP](https://github.com/mbailey/voicemode) | Natural voice conversations with Claude Code via Whisper + Kokoro |
| 12 | [Awesome Claude Plugins](https://github.com/ComposioHQ/awesome-claude-plugins) | 9,000+ repos indexed with adoption metrics — find what people actually install |

---

## 🗂️ How to Update This Repo

See [RESOURCES.md](./RESOURCES.md) for the full step-by-step guide on keeping this repository up to date.

---

## 🔗 Official Claude Code Links

- 📖 [Claude Code Docs](https://docs.claude.com/en/docs/claude-code/overview)
- 📦 [npm Package](https://www.npmjs.com/package/@anthropic-ai/claude-code)
- 🌐 [Anthropic](https://www.anthropic.com)

---

*Last updated: April 2026*

## Dynamic Post-Processing Block-Sizer (DBS) Simulation
The pipeline generates a set of reports and figures detailing the simulation results:

### Figures
- `outputs/figures/01_rtt_distribution.png`: Histogram of the RTT latency distribution.
- `outputs/figures/02_qber_distribution.png`: Histogram of synthetic QBER.
- `outputs/figures/03_correlation_heatmap.png`: Heatmap showing correlation between RTT, QBER, SKR, and T2K.
- `outputs/figures/04_skr_distribution_comparison.png`: KDE plot comparing SKR distributions across policies.
- `outputs/figures/05_t2k_distribution_comparison.png`: KDE plot comparing T2K distributions across policies.
- `outputs/figures/06_rtt_vs_skr_dbs_scatter.png`: Scatter plot showing SKR under DBS against RTT.
- `outputs/figures/07_qber_vs_skr_dbs_scatter.png`: Scatter plot showing SKR under DBS against QBER.
- `outputs/figures/08_skr_by_latency_regime_bar.png`: Bar plot comparing mean SKR across policies in high/low latency regimes.
- `outputs/figures/09_t2k_by_latency_regime_bar.png`: Bar plot comparing mean T2K across policies in high/low latency regimes.
- `outputs/figures/10_skr_temporal_trend_ma.png`: Moving average trend line of SKR over time.

### Tables
- `outputs/tables/01_descriptive_statistics.csv`: Summary statistics for numeric variables.
- `outputs/tables/02_data_quality_report.csv`: Data quality metrics including null counts and distinct values.
- `outputs/tables/03_correlation_matrix.csv`: Full correlation matrix for numeric columns.
- `outputs/tables/04_skr_policy_comparison.csv`: Summary statistics comparing SKR for DBS, Large, and Small policies.
- `outputs/tables/05_t2k_policy_comparison.csv`: Summary statistics comparing T2K for DBS, Large, and Small policies.
- `outputs/tables/06_metrics_by_latency_regime.csv`: Mean SKR and T2K grouped by high/low latency regimes.
- `outputs/tables/07_skr_by_qber_bins.csv`: Mean SKR across different binned ranges of QBER.
- `outputs/tables/08_top_10_blocks_skr_dbs.csv`: The top 10 best-performing blocks by SKR under DBS.
- `outputs/tables/09_worst_10_blocks_skr_dbs.csv`: The 10 worst-performing blocks by SKR under DBS.
- `outputs/tables/10_key_availability_summary.csv`: Percentage of blocks with SKR > 0 across policies.
