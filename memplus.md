---

## 🔧 Reference Tools & Resources

### Token Optimization Tools (for Claude Code sessions)

Use these to reduce context window waste and cut API costs:

| Tool | What it does | Savings | Repo |
|------|-------------|---------|------|
| Caveman Claude | Makes Claude use minimal output tokens | ~75% output tokens | https://github.com/juliusbrussee/… ⚠️ |
| RTK (Rust Token Killer) | Proxy that filters terminal output | 60–90% | https://github.com/rtk-ai/rtk |
| Code Review Graph | Tree-sitter graph so Claude reads only relevant code | ~49x on large repos | https://github.com/tirth8205/code… ⚠️ |
| Context Mode | Sandboxes logs/GitHub output into SQLite | ~98% context reduction | https://github.com/mksglu/context… ⚠️ |
| Claude Token Optimizer | CLAUDE.md prompts that optimize any project | ~90% (11K → 1.3K docs) | https://github.com/nadimtuhin/cla… ⚠️ |
| Token Optimizer | Detects and removes ghost tokens | Context quality restore | https://github.com/alexgreensh/to… ⚠️ |
| Token Optimizer MCP | Aggressive caching + compression for MCP tools | 95%+ via MCP | https://github.com/ooples/token-o… ⚠️ |
| Claude Context (Zilliz) | Hybrid vector search MCP for full codebase context | ~40% cost reduction | https://github.com/zilliztech/cla… ⚠️ |
| Claude Token Efficient | Drop-in CLAUDE.md enforcing strict terseness | ~90% with zero code changes | https://github.com/drona23/claude… ⚠️ |
| Token Savior | Symbol-based navigation, not full file reads | ~97% on code navigation | https://github.com/mibayy/token-s… ⚠️ |

#### Recommended combos
- Massive repo → Code Review Graph + Token Savior
- Heavy terminal output → RTK
- MCP data dumps → Context Mode
- Instant fix → Caveman Claude + Claude Token Efficient

---

### 🚀 Trending AI/Agent Projects (April 2026)

Useful references and inspiration for agentic workflows:

| Project | Description | Stars | Repo |
|---------|-------------|-------|------|
| andrej-karpathy-skills | Single CLAUDE.md distilled from Karpathy's workflows | 48K⭐ | https://github.com/forrestchang/a… ⚠️ |
| claude-mem | Captures, compresses and reinjects session memory | 59K⭐ | https://github.com/thedotmack/cla… ⚠️ |
| voicebox | Open-source voice synthesis studio (ElevenLabs alternative) | 18K⭐ | https://github.com/jamiepine/voic… ⚠️ |
| open-agents (Vercel) | Self-hosted cloud agent deployment platform | 3.1K⭐ | https://github.com/vercel-labs/op… ⚠️ |
| cognee | Agent memory engine (~6 lines setup) | 15K⭐ | https://github.com/topoteretes/cognee |
| magika (Google) | AI-based file type detection | 14K⭐ | https://github.com/google/magika |
| GenericAgent | Self-evolving agent with skill trees, 6x fewer tokens | 2.6K⭐ | https://github.com/lsdefine/Gener… ⚠️ |
| omi | Screen + audio awareness agent | 8.9K⭐ | https://github.com/BasedHardware/… ⚠️ |
| evolver | Agents that evolve/optimize themselves | 3K⭐ | https://github.com/EvoMap/evolver |

---

> ⚠️ URLs marked with ⚠️ were truncated in the source — resolve full paths before use.
