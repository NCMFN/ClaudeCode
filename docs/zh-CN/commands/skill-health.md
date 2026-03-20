---
name: skill-health
description: 显示技能组合健康仪表盘，包含图表和分析功能
command: true
---

# 技能健康仪表板

显示投资组合中所有技能的全面健康仪表板，包含成功率走势图、故障模式聚类、待处理修订和版本历史。

## 实现

以仪表板模式运行技能健康 CLI：

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/skills-health.js" --dashboard
```

仅针对特定面板：

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/skills-health.js" --dashboard --panel failures
```

如需机器可读输出：

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/skills-health.js" --dashboard --json
```

## 用法

```
/skill-health                    # Full dashboard view
/skill-health --panel failures   # Only failure clustering panel
/skill-health --json             # Machine-readable JSON output
```

## 操作步骤

1. 使用 --dashboard 标志运行 skills-health.js 脚本
2. 向用户显示输出
3. 如果有任何技能表现下降，高亮显示并建议运行 /evolve
4. 如果有待处理的修订，建议进行审查

## 面板

* **成功率 (30天)** — 显示每个技能每日成功率的走势图
* **故障模式** — 按水平条形图聚类的故障原因
* **待处理修订** — 等待审查的修订提案
* **版本历史** — 每个技能的版本快照时间线
