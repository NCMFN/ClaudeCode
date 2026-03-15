---
name: team-builder
description: Interactive agent picker — browse available agents by domain, compose custom teams, and dispatch them in parallel on a task. Use when saying "team builder", "pick agents", "assemble team", or "browse agents".
origin: community
---

# Team Builder

Interactive menu for browsing and composing agent teams on demand. Works with any collection of agent markdown files organized by domain subdirectories.

## When to Use

- You have multiple agent personas (markdown files) and want to pick which ones to use for a task
- You want to compose an ad-hoc team from different domains (e.g., Security + SEO + Architecture)
- You want to browse what agents are available before deciding

## Prerequisites

Agent files must be organized as markdown files in subdirectories by domain:

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

Each file should contain a persona prompt (identity, rules, workflow, deliverables). The first `# Heading` is used as the agent name and the first paragraph as the description.

## Process

### Step 1: Discover Available Agents

Glob `agents/**/*.md` (or the user's configured agent directory). Exclude README files. For each file:
- Extract the domain from the subdirectory name
- Extract the agent name from the first `# Heading`
- Extract a one-line summary from the first paragraph after the heading

### Step 2: Present Domain Menu

```
Available agent domains:
1. Engineering — Software Architect, Security Engineer
2. Marketing — SEO Specialist
3. Sales — Discovery Coach, Outbound Strategist

Pick domains or name specific agents (e.g., "1,3" or "security + seo"):
```

- Skip domains with zero agents (empty directories)
- Show agent count per domain

### Step 3: Handle Selection

Accept flexible input:
- Numbers: "1,3" selects all agents from Engineering and Sales
- Names: "security + seo" fuzzy-matches against discovered agents
- "all from engineering" selects every agent in that domain

Confirm selection:
```
Selected: Security Engineer + SEO Specialist
What should they work on? (describe the task):
```

### Step 4: Spawn Agents in Parallel

1. Read each selected agent's markdown file
2. Prompt for the task description if not already provided
3. Spawn all agents in parallel using the Agent tool:
   - `subagent_type: "general-purpose"`
   - `prompt: "{agent file content}\n\nTask: {task description}"`
   - Each agent runs independently — no inter-agent communication needed

### Step 5: Synthesize Results

Collect all outputs and present a unified report:
- Results grouped by agent
- Synthesis section highlighting:
  - Agreements across agents
  - Conflicts or tensions between recommendations
  - Recommended next steps

If only 1 agent was selected, skip synthesis and present the output directly.

## Configuration

The agent directory path should be set to wherever your agent markdown files live. Common locations:

- `~/.claude/agents/` — Claude Code global agents
- `./agents/` — project-local agents
- Any custom path with markdown persona files

## Rules

- **Dynamic discovery only.** Never hardcode agent lists. New files in the directory auto-appear in the menu.
- **Max 5 agents per team.** More than 5 produces diminishing returns and excessive token usage.
- **Parallel dispatch.** All agents run simultaneously — use the Agent tool's parallel invocation pattern.
- **No TeamCreate needed.** Ad-hoc teams use parallel Agent calls. Reserve TeamCreate for pre-built teams where agents need to debate or respond to each other.

## Example Usage

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
