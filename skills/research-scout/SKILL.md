---
name: research-scout
description: Autonomously scouts for new information that challenges or updates existing project knowledge. Searches web, Reddit, Hacker News, and Quora for new strategies, tools, announcements, and workflow changes. Cross-references findings against existing docs, discards redundant items, and stores validated discoveries in long-term-memory.md. Designed to run unattended on a schedule — 3x nightly for new findings, weekly for memory promotion.
origin: ECC
---

# Research Scout

Continuously hunt for new information that challenges or extends what the project already knows. Run unattended on a schedule; surface only what is genuinely new.

## When to Activate

- Scheduled nightly run (new-findings sweep)
- Scheduled weekly run (memory promotion pass)
- User says "scout for new info", "check what's changed", "update my knowledge", or "run research scout"
- After a major external release (new Claude model, Remotion version, etc.) to capture immediate community reactions

## Overview

The skill has two modes:

| Mode | Trigger | Job |
|------|---------|-----|
| **Scout** | 3× nightly | Search for new findings, cross-reference, append validated items to `new_learnings` |
| **Promote** | Weekly | Review `new_learnings`, merge confirmed patterns into main memory files, clear staging |

---

## Mode 1 — Scout (Nightly)

### Step 1: Build Search Queries from Project Context

Read the project's existing documentation to understand what is already known:

```
Files to scan (in order of priority):
1. CLAUDE.md                          ← project instructions
2. .claude/research/*.md              ← research playbooks
3. .claude/homunculus/instincts/**    ← learned instincts
4. skills/*/SKILL.md                  ← existing skill knowledge (sample 5–10)
5. long-term-memory.md                ← previous findings (if exists)
```

Extract 5–8 query themes from what you find. Examples for this repo:
- "Claude Code new features 2025"
- "Remotion React video framework updates"
- "AI coding agent workflow improvements"
- "Claude hooks MCP server patterns"
- "everything-claude-code plugin new release"

### Step 2: Search Across Sources

Run queries across all four sources. Use `WebSearch` for general web; use targeted site: searches for communities.

```
Web (general):
  WebSearch("<theme> site:github.com OR site:anthropic.com OR site:docs.remotion.dev")
  WebSearch("<theme> announcement OR release OR deprecation")

Reddit:
  WebSearch("<theme> site:reddit.com/r/ClaudeAI OR site:reddit.com/r/LocalLLaMA OR site:reddit.com/r/MachineLearning")
  WebSearch("<theme> site:reddit.com -is:comment")

Hacker News:
  WebSearch("<theme> site:news.ycombinator.com")
  WebSearch("<theme> site:hn.algolia.com")

Quora:
  WebSearch("<theme> site:quora.com")
```

Collect raw findings: title, URL, date (if visible), and a one-line summary of what it says.

### Step 3: Cross-Reference Against Existing Docs

For each raw finding, check whether the project already covers it:

```
REDUNDANT  → already documented, same recommendation, same API, skip
ADDITIVE   → new detail, flag, or option not yet mentioned, keep
CONTRADICTORY → conflicts with current guidance (e.g. deprecated API, better pattern), keep + flag as ⚠️
UNRELATED  → no relevance to project scope, discard
```

Discard REDUNDANT and UNRELATED findings immediately. Only ADDITIVE and CONTRADICTORY findings proceed to storage.

### Step 4: Write to `new_learnings` in `long-term-memory.md`

Append each validated finding as a structured entry. Create `long-term-memory.md` at the repo root if it does not exist.

```markdown
## new_learnings

<!-- Entries appended by research-scout. Do not edit manually. -->

### <ISO-8601 timestamp> — <one-line title>

- **Source:** <URL>
- **Type:** ADDITIVE | CONTRADICTORY ⚠️
- **Finding:** <One sentence: what it says>
- **Impact:** <One sentence: what it changes or adds to the project>
- **Status:** staging
```

Example:

```markdown
### 2025-10-14T02:17:00Z — Remotion 4.0 removes `@remotion/transitions` peer dep

- **Source:** https://github.com/remotion-dev/remotion/releases/tag/v4.0.0
- **Type:** CONTRADICTORY ⚠️
- **Finding:** @remotion/transitions is now bundled inside `remotion` core; no separate install needed.
- **Impact:** Update `remotion-best-practices` SKILL.md to remove the separate install step.
- **Status:** staging
```

Rules:
- One entry per finding, no batching
- Always include the source URL — no URL means discard
- `Status: staging` on all new entries; never touch existing entries during Scout mode
- If `long-term-memory.md` does not exist, create it with a top-level header before appending

---

## Mode 2 — Weekly Memory Promotion

### Step 1: Review `new_learnings`

Read every entry with `Status: staging` in `long-term-memory.md`. For each:

1. Re-check the source URL is still reachable (`WebFetch` the URL, check for 404 or content change)
2. Re-read the relevant skill or doc file to confirm the finding is still new/contradictory
3. Classify:
   - **Confirm** → finding is valid, source still live, still relevant
   - **Stale** → source gone (404), or project already addressed it in the meantime
   - **Needs more data** → only one source, not yet confirmed by a second

### Step 2: Promote Confirmed Findings

For each **Confirmed** finding:

1. Locate the target file (skill, rule, memory file, or research playbook)
2. Make the minimal edit that incorporates the new knowledge:
   - Add a note, update a version number, add an anti-pattern, or flag a deprecation
   - Keep changes narrow — do not refactor surrounding content
3. Update the entry in `new_learnings`: change `Status: staging` → `Status: promoted` and add `Promoted-to: <file>:<line-range>`

For **Stale** entries: change `Status: staging` → `Status: stale`.

For **Needs more data** entries: leave as `Status: staging`, add `Note: needs second source`.

### Step 3: Clear Staging

After processing all entries:

1. Move all `Status: promoted` and `Status: stale` entries from `new_learnings` into a `## learning_archive` section at the bottom of `long-term-memory.md`
2. Leave only `Status: staging` entries in the `new_learnings` section
3. Add a promotion-run header:

```markdown
### Promotion run: <ISO-8601 date>
Promoted: N | Stale: N | Pending: N
```

---

## Memory File Locations

| File | Purpose |
|------|---------|
| `long-term-memory.md` (repo root) | Primary staging + archive store |
| `skills/*/SKILL.md` | Target for skill-level promotions |
| `.claude/research/*.md` | Target for research playbook promotions |
| `.claude/rules/*.md` | Target for rule promotions |

Never create files outside this list without user approval.

---

## Search Source Guide

| Source | Best for | Query pattern |
|--------|----------|---------------|
| GitHub releases / changelogs | Version bumps, breaking changes | `site:github.com <project> release` |
| Anthropic docs / blog | Claude API, models, new features | `site:anthropic.com <topic>` |
| Reddit r/ClaudeAI | Community-discovered gotchas | `site:reddit.com/r/ClaudeAI <topic>` |
| Reddit r/LocalLLaMA | Model comparisons, tooling | `site:reddit.com/r/LocalLLaMA <topic>` |
| Hacker News | Launch announcements, critiques | `site:news.ycombinator.com <topic>` |
| Quora | Beginner-level confusion patterns | `site:quora.com <topic>` |

Prioritise recency: filter results to the last 30 days where possible. Discard results older than 90 days unless they are in a changelog or official doc.

---

## Anti-Patterns

- **Storing redundant findings** — always cross-reference first; bloated staging dilutes signal
- **Promoting without re-verification** — the weekly pass must re-check the source, not just trust the Scout entry
- **Editing more than the target** — a promotion touches one file, one fact; do not refactor surrounding content
- **Missing source URL** — every entry must have a traceable URL; anonymous or paraphrased claims are discarded
- **Running Scout and Promote in the same pass** — keep modes separate; Scout appends, Promote reviews

---

## Scheduling

This skill is designed to run as a remote agent on a cron schedule:

| Schedule | Mode | Cron expression |
|----------|------|----------------|
| 10 PM nightly | Scout | `0 22 * * *` |
| 2 AM nightly | Scout | `0 2 * * *` |
| 5 AM nightly | Scout | `0 5 * * *` |
| Sunday 8 AM | Promote | `0 8 * * 0` |

Start each scheduled run with: `Use the research-scout skill. Run in Scout mode.` or `Use the research-scout skill. Run in Promote mode.`

## Related Skills

- `deep-research` — human-driven deep research with citations; use for one-off topics
- `market-research` — competitive and market analysis
- `continuous-learning` — session-level pattern extraction into learned skills
- `continuous-learning-v2` — enhanced learning with instinct file integration
