# 工具链审计命令

运行确定性仓库工具审计并返回优先级评分卡。

## 使用方式

`/harness-audit [scope] [--format text|json]`

* `scope` (可选): `repo` (默认), `hooks`, `skills`, `commands`, `agents`
* `--format`: 输出样式 (`text` 默认, `json` 用于自动化)

## 确定性引擎

始终运行：

```bash
node scripts/harness-audit.js <scope> --format <text|json>
```

此脚本是评分和检查的真相来源。请勿发明额外的维度或临时评分点。

评分标准版本：`2026-03-16`。

该脚本计算7个固定类别（每个类别 `0-10` 进行归一化）：

1. 工具覆盖度
2. 上下文效率
3. 质量门禁
4. 记忆持久化
5. 评估覆盖度
6. 安全护栏
7. 成本效率

分数源自明确的文件/规则检查，并且对于同一提交是可重现的。

## 输出约定

返回：

1. `overall_score` 分，满分 `max_score` 分（`repo` 对应70分；范围更小的审计对应更小的满分）
2. 类别分数及具体发现项
3. 失败的检查及其精确文件路径
4. 来自确定性输出的前3项操作（`top_actions`）
5. 建议接下来应用的ECC技能

## 检查清单

* 直接使用脚本输出；请勿手动重新评分。
* 如果请求 `--format json`，则原样返回脚本JSON。
* 如果请求文本输出，则总结失败的检查和首要操作。
* 包含来自 `checks[]` 和 `top_actions[]` 的精确文件路径。

## 结果示例

```text
Harness Audit (repo): 66/70
- Tool Coverage: 10/10 (10/10 pts)
- Context Efficiency: 9/10 (9/10 pts)
- Quality Gates: 10/10 (10/10 pts)

Top 3 Actions:
1) [Security Guardrails] Add prompt/tool preflight security guards in hooks/hooks.json. (hooks/hooks.json)
2) [Tool Coverage] Sync commands/harness-audit.md and .opencode/commands/harness-audit.md. (.opencode/commands/harness-audit.md)
3) [Eval Coverage] Increase automated test coverage across scripts/hooks/lib. (tests/)
```

## 参数

$ARGUMENTS:

* `repo|hooks|skills|commands|agents` (可选范围)
* `--format text|json` (可选输出格式)
