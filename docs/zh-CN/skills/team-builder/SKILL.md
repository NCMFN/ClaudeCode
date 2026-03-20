---
name: team-builder
description: 用于组合和派遣并行团队的交互式代理选择器
origin: community
---

# 团队构建器

用于按需浏览和组合智能体团队的交互式菜单。适用于扁平化或按领域子目录组织的智能体集合。

## 何时使用

* 您有多个智能体角色（markdown 文件），并希望为某项任务选择使用哪些
* 您希望从不同领域（例如，安全 + SEO + 架构）组合一个临时团队
* 您希望在决定前浏览有哪些可用的智能体

## 先决条件

智能体文件必须是包含角色提示（身份、规则、工作流程、交付成果）的 markdown 文件。第一个 `# Heading` 被用作智能体名称，第一个段落被用作描述。

支持扁平化和子目录两种布局：

**子目录布局** — 领域从文件夹名称推断：

```
agents/
├── engineering/
│   ├── security-engineer.md
│   └── software-architect.md
├── marketing/
│   └── seo-specialist.md
└── sales/
    └── discovery-coach.md
```

**扁平布局** — 领域从共享的文件名前缀推断。当 2 个或更多文件共享前缀时，该前缀算作一个领域。具有唯一前缀的文件归入“通用”类别。注意：算法在第一个 `-` 处分割，因此多词领域（例如 `product-management`）应使用子目录布局：

```
agents/
├── engineering-security-engineer.md
├── engineering-software-architect.md
├── marketing-seo-specialist.md
├── marketing-content-strategist.md
├── sales-discovery-coach.md
└── sales-outbound-strategist.md
```

## 配置

按顺序探测智能体目录并合并结果：

1. `./agents/**/*.md` + `./agents/*.md` — 项目本地智能体（两个深度）
2. `~/.claude/agents/**/*.md` + `~/.claude/agents/*.md` — 全局智能体（两个深度）

来自所有位置的结果会被合并，并按智能体名称去重。项目本地智能体优先于同名的全局智能体。如果用户指定，可以使用自定义路径代替。

## 工作原理

### 步骤 1：发现可用智能体

使用上述探测顺序对智能体目录进行全局搜索。排除 README 文件。对于找到的每个文件：

* **子目录布局：** 从父文件夹名称提取领域
* **扁平布局：** 收集所有文件名前缀（第一个 `-` 之前的文本）。一个前缀仅在出现在 2 个或更多文件名中时才符合领域资格（例如，`engineering-security-engineer.md` 和 `engineering-software-architect.md` 都以 `engineering` 开头 → 工程领域）。具有唯一前缀的文件（例如 `code-reviewer.md`、`tdd-guide.md`）被归入“通用”类别
* 从第一个 `# Heading` 提取智能体名称。如果未找到标题，则从文件名派生名称（去除 `.md`，用空格替换连字符，转换为标题大小写）
* 从标题后的第一个段落提取一行摘要

如果在探测所有位置后未找到智能体文件，则通知用户：“未找到智能体文件。已检查：\[探测的路径列表]。预期：这些目录之一的 markdown 文件。”然后停止。

### 步骤 2：呈现领域菜单

```
Available agent domains:
1. Engineering — Software Architect, Security Engineer
2. Marketing — SEO Specialist
3. Sales — Discovery Coach, Outbound Strategist

Pick domains or name specific agents (e.g., "1,3" or "security + seo"):
```

* 跳过智能体数为零的领域（空目录）
* 显示每个领域的智能体数量

### 步骤 3：处理选择

接受灵活的输入：

* 数字：“1,3” 选择工程和销售领域的所有智能体
* 名称：“security + seo” 对发现的智能体进行模糊匹配
* “all from engineering” 选择该领域的每个智能体

如果选择了超过 5 个智能体，则按字母顺序列出它们，并要求用户缩小范围：“您选择了 N 个智能体（最多 5 个）。请选择保留哪些，或说 'first 5' 以使用按字母顺序的前五个。”

确认选择：

```
Selected: Security Engineer + SEO Specialist
What should they work on? (describe the task):
```

### 步骤 4：并行生成智能体

1. 读取每个选定智能体的 markdown 文件
2. 如果尚未提供，则提示输入任务描述
3. 使用智能体工具并行生成所有智能体：
   * `subagent_type: "general-purpose"`
   * `prompt: "{agent file content}\n\nTask: {task description}"`
   * 每个智能体独立运行 — 无需智能体间通信
4. 如果某个智能体失败（错误、超时或空输出），则内联注明失败（例如，“安全工程师：失败 — \[原因]”），并继续处理成功智能体的结果

### 步骤 5：综合结果

收集所有输出并呈现统一报告：

* 结果按智能体分组
* 综合部分重点说明：
  * 各智能体间的共识
  * 建议间的冲突或矛盾
  * 建议的后续步骤

如果只选择了 1 个智能体，则跳过综合部分，直接呈现输出。

## 规则

* **仅动态发现。** 切勿硬编码智能体列表。目录中的新文件会自动出现在菜单中。
* **每个团队最多 5 个智能体。** 超过 5 个会产生收益递减和过多的令牌使用。在选择时强制执行。
* **并行分发。** 所有智能体同时运行 — 使用智能体工具的并行调用模式。
* **并行智能体调用，而非 TeamCreate。** 此技能使用并行智能体工具调用来进行独立工作。TeamCreate（一个用于多智能体对话的 Claude Code 工具）仅在智能体必须辩论或相互回应时才需要。

## 示例

```
User: team builder

Claude:
Available agent domains:
1. Engineering (2) — Software Architect, Security Engineer
2. Marketing (1) — SEO Specialist
3. Sales (4) — Discovery Coach, Outbound Strategist, Proposal Strategist, Sales Engineer
4. Support (1) — Executive Summary

Pick domains or name specific agents:

User: security + seo

Claude:
Selected: Security Engineer + SEO Specialist
What should they work on?

User: Review my Next.js e-commerce site before launch

[Both agents spawn in parallel, each applying their specialty to the codebase]

Claude:
## Security Engineer Findings
- [findings...]

## SEO Specialist Findings
- [findings...]

## Synthesis
Both agents agree on: [...]
Tension: Security recommends CSP that blocks inline styles, SEO needs inline schema markup. Resolution: [...]
Next steps: [...]
```
