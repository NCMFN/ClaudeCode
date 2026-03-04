# Everything Claude Code — Personal Fork

> Forked from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) by [@affaanmustafa](https://x.com/affaanmustafa) — Anthropic Hackathon Winner.
> This fork is customized for personal use with Hexagonal Architecture, DDD, and Clean Code enforcement added on top of the original system.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## What This Is

A Claude Code plugin — a collection of production-ready agents, skills, hooks, commands, and rules for software development. This fork adds an opinionated architecture layer on top of the upstream:

- **Hexagonal Architecture + DDD** enforced by a strategic architect agent
- **Clean Architecture + Clean Code** enforced by an Uncle Bob consultant agent
- **Module-level design** handled by a dedicated module architect agent

---

## Repository Structure

```
everything-claude-code/
│
├── agents/                          # Specialized subagents for delegation
│   ├── architect.md                 # ★ Hexagonal Architecture + DDD enforcer (system-level)
│   ├── architect-module.md          # ★ Module-level design within hexagonal boundaries
│   ├── uncle-bob.md                 # ★ Clean Architecture + Clean Code consultant
│   ├── planner.md                   # Feature planning, risk assessment, phase breakdown
│   ├── code-reviewer.md             # Security, quality, and Clean Code review
│   ├── tdd-guide.md                 # Test-driven development workflow
│   ├── security-reviewer.md         # OWASP / vulnerability analysis
│   ├── refactor-cleaner.md          # Dead code detection and safe removal
│   └── doc-updater.md               # Documentation sync
│
├── skills/                          # Domain knowledge invoked by agents or commands
│   ├── tdd-workflow/
│   ├── security-review/
│   ├── backend-patterns/
│   ├── frontend-patterns/
│   ├── continuous-learning/
│   ├── autonomous-loops/
│   └── ...50+ more
│
├── commands/                        # Slash commands (/plan, /tdd, /code-review, ...)
│   ├── plan.md
│   ├── tdd.md
│   ├── code-review.md
│   ├── build-fix.md
│   ├── e2e.md
│   ├── refactor-clean.md
│   └── ...30+ more
│
├── rules/                           # Always-follow guidelines (copy to ~/.claude/rules/)
│   ├── common/                      # Language-agnostic — always install
│   │   ├── coding-style.md
│   │   ├── git-workflow.md
│   │   ├── testing.md
│   │   ├── security.md
│   │   └── agents.md
│   ├── typescript/
│   ├── python/
│   └── golang/
│
├── hooks/                           # Trigger-based automations
│   └── hooks.json                   # PreToolUse, PostToolUse, Stop, SessionStart events
│
├── scripts/                         # Cross-platform Node.js hook implementations
│   ├── lib/
│   │   ├── utils.js
│   │   └── package-manager.js
│   └── hooks/
│       ├── session-start.js
│       ├── session-end.js
│       └── evaluate-session.js
│
├── contexts/                        # Dynamic system prompt injection
│   ├── dev.md
│   ├── review.md
│   └── research.md
│
├── mcp-configs/
│   └── mcp-servers.json             # GitHub, Supabase, Vercel, Railway, ...
│
├── examples/                        # CLAUDE.md templates for real-world stacks
│   ├── saas-nextjs-CLAUDE.md
│   ├── go-microservice-CLAUDE.md
│   └── django-api-CLAUDE.md
│
└── tests/
    └── run-all.js
```

> ★ = added or heavily modified in this fork

---

## Agent Orchestration

### Full Development Flow

```mermaid
flowchart TD
    USER(["User Request"])

    USER --> PLANNER["planner\nBreaks task into phases\nidentifies risks"]

    PLANNER --> ARCH["architect\nDefines hexagonal structure\nBounded contexts, ports, aggregates\nDDD model"]

    ARCH --> ARCHMOD["architect-module\nDesigns module internals\nPattern selection\nCode organization"]

    ARCHMOD --> UB1["uncle-bob\nPre-implementation review\nSOLID + Clean Architecture\nDependency rule audit"]

    UB1 -->|"SOLID violations\nClean Code prescriptions"| ARCHMOD
    UB1 -->|"Layer violations\nPort contract issues"| ARCH

    UB1 -->|"Design approved"| CODE["Code written\nby Claude Code"]

    CODE --> CR["code-reviewer\nSecurity, quality\nbest practices"]
    CODE --> UB2["uncle-bob\nPost-implementation\nNaming, functions, tests\nClean Code audit"]

    CR --> REPORT["Merged Review Report\n[Security] findings\n[Clean Code] findings\n[Clean Architecture] findings"]
    UB2 --> REPORT

    REPORT -->|"Blockers found"| CODE
    REPORT -->|"All clear"| DONE(["Ready to commit"])
```

### Architecture Agent Chain

```mermaid
flowchart LR
    ARCH["architect\n(Strategic)"]
    ARCHMOD["architect-module\n(Tactical)"]
    UB["uncle-bob\n(Consultant)"]

    ARCH -->|"Layer assignment\nPort contracts\nDDD constraints"| ARCHMOD
    ARCHMOD -->|"Calls after\ndesign proposal"| UB
    UB -->|"SOLID + Clean Code\nprescriptions"| ARCHMOD
    UB -->|"Layer/boundary\nviolations"| ARCH
    ARCHMOD -->|"Escalates boundary\ndecisions"| ARCH

    style ARCH fill:#1a1a2e,color:#fff
    style ARCHMOD fill:#16213e,color:#fff
    style UB fill:#0f3460,color:#fff
```

### Responsibilities Split

| Agent | Scope | Enforces |
|---|---|---|
| **architect** | System-wide | Hexagonal Architecture, DDD strategic (bounded contexts, aggregates, ports) |
| **architect-module** | Single layer/module | Module internals, pattern selection, code efficiency |
| **uncle-bob** | Design + code | SOLID, Clean Architecture dependency rule, Clean Code (naming, functions, tests) |
| **planner** | Feature scope | Implementation phases, risk assessment |
| **code-reviewer** | Changed code | Security, quality, regressions |

---

## Complex Task Flows

### Feature Development (Full Lifecycle)

```mermaid
sequenceDiagram
    actor User
    participant planner
    participant architect
    participant architect-module
    participant uncle-bob
    participant code-reviewer

    User->>planner: /plan "Add feature X"
    planner->>planner: Analyze requirements, risks, phases
    planner-->>User: Implementation plan (waits for confirmation)

    User->>architect: Confirm → design architecture
    architect->>architect: Define bounded contexts, aggregates, ports
    architect->>architect-module: Delegate module design with constraints

    architect-module->>architect-module: Design internals, select patterns
    architect-module->>uncle-bob: Pre-implementation design review
    uncle-bob-->>architect-module: SOLID prescriptions
    uncle-bob-->>architect: Layer violations (if any)

    architect-module-->>User: Approved design

    User->>User: Implement code (guided by /tdd)

    User->>code-reviewer: /code-review
    code-reviewer->>uncle-bob: Delegate Clean Code audit
    uncle-bob-->>code-reviewer: [Clean Code] + [Clean Architecture] findings
    code-reviewer-->>User: Merged report (Security + Quality + Clean Code)
```

### TDD Workflow

```mermaid
flowchart TD
    START(["Feature to implement"]) --> INTERFACE["1. Define interfaces\nDomain ports + types"]

    INTERFACE --> RED["2. RED\nWrite failing tests\nagainst the interface"]

    RED --> GREEN["3. GREEN\nMinimal implementation\nto pass tests"]

    GREEN --> CHECK{Tests pass?}
    CHECK -->|No| GREEN
    CHECK -->|Yes| REFACTOR["4. REFACTOR\nClean up\nno behavior change"]

    REFACTOR --> COVERAGE{Coverage ≥ 80%?}
    COVERAGE -->|No| RED
    COVERAGE -->|Yes| UB["uncle-bob review\nClean Code audit\non final implementation"]

    UB --> ISSUES{Issues found?}
    ISSUES -->|CRITICAL/HIGH| REFACTOR
    ISSUES -->|Clear| DONE(["Commit"])
```

### Security Review Flow

```mermaid
flowchart LR
    CODE["Changed code"] --> CR["code-reviewer"]

    CR --> SEC["Security checklist\nOWASP Top 10\nHardcoded credentials\nSQL injection / XSS\nInput validation"]

    CR --> UB["uncle-bob\nClean Architecture\ndependency rule\nSOLID violations"]

    CR --> QUAL["Quality checklist\nFunctions > 50 lines\nNesting depth > 4\nMissing error handling\nTODO comments"]

    SEC --> MERGE["Merged Report"]
    UB --> MERGE
    QUAL --> MERGE

    MERGE --> BLOCK{CRITICAL or HIGH?}
    BLOCK -->|Yes| FIX["Fix required\nbefore merge"]
    BLOCK -->|No| APPROVE["Approved"]
```

### Refactoring Flow

```mermaid
flowchart TD
    START(["Refactor request"]) --> ARCH["architect\nValidate current vs\ntarget hexagonal structure"]

    ARCH --> UB["uncle-bob\nAudit existing code\nfor SOLID violations"]

    UB --> PLAN["architect-module\nDesign refactor plan\nwithin approved boundaries"]

    PLAN --> TESTS["Run full test suite\nEstablish baseline"]

    TESTS --> SAFE["Identify SAFE items\n(unused code, dead exports)"]
    SAFE --> DELETE["Remove one category\nat a time"]
    DELETE --> VERIFY["Re-run tests"]

    VERIFY --> PASS{Tests pass?}
    PASS -->|No| REVERT["git checkout -- file\nskip this item"]
    PASS -->|Yes| MORE{More items?}

    MORE -->|Yes| DELETE
    MORE -->|No| UB2["uncle-bob final review\nClean Code audit\non refactored code"]

    UB2 --> COMMIT(["Commit"])
    REVERT --> MORE
```

---

## Key Concepts

### Agents

Subagents handle delegated tasks with limited scope. Defined as Markdown with YAML frontmatter:

```markdown
---
name: architect
description: Strategic architect enforcing Hexagonal Architecture and DDD...
tools: ["Read", "Grep", "Glob", "Agent"]
model: opus
---
```

### Skills

Domain knowledge invoked by commands or agents. Markdown files describing when to use, how it works, examples:

```
skills/tdd-workflow/SKILL.md
skills/security-review/SKILL.md
skills/backend-patterns/SKILL.md
```

### Hooks

Automated triggers on tool events (`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`):

```json
{
  "matcher": "tool == \"Edit\"",
  "hooks": [{
    "type": "command",
    "command": "node scripts/hooks/post-edit.js"
  }]
}
```

### Rules

Always-follow guidelines, installed to `~/.claude/rules/`:

```
rules/common/          # Language-agnostic (always install)
rules/typescript/      # TS/JS specific
rules/python/          # Python specific
rules/golang/          # Go specific
```

---

## Installation

```bash
# Clone
git clone <this-repo>
cd everything-claude-code

# Copy agents
cp agents/*.md ~/.claude/agents/

# Copy rules (common + your stack)
cp -r rules/common/* ~/.claude/rules/
cp -r rules/typescript/* ~/.claude/rules/   # pick your stack

# Copy commands
cp commands/*.md ~/.claude/commands/

# Copy skills (selective — only what you need)
cp -r skills/tdd-workflow ~/.claude/skills/
cp -r skills/security-review ~/.claude/skills/
cp -r skills/backend-patterns ~/.claude/skills/
```

Or use the installer:

```bash
./install.sh typescript    # installs common + typescript rules
```

---

## Key Commands

| Command | What it does | Agents involved |
|---|---|---|
| `/plan` | Implementation plan, risks, phases | planner |
| `/tdd` | Test-driven development workflow | tdd-guide |
| `/code-review` | Security + quality review | code-reviewer + uncle-bob |
| `/build-fix` | Fix build errors | build-error-resolver |
| `/e2e` | Generate + run E2E tests | e2e-runner |
| `/refactor-clean` | Remove dead code safely | refactor-cleaner |
| `/verify` | Run verification loop | — |
| `/learn` | Extract patterns from session | — |

---

## Running Tests

```bash
node tests/run-all.js
```

---

## Credits

Original project: **[affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code)** by [@affaanmustafa](https://x.com/affaanmustafa).
Built from an Anthropic Hackathon winner. 50K+ stars, 30+ contributors, 6 languages supported.

Guides from the original author:
- [Shorthand Guide](https://x.com/affaanmustafa/status/2012378465664745795) — setup, foundations, philosophy
- [Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) — token optimization, memory, evals, parallelization

---

## License

MIT
