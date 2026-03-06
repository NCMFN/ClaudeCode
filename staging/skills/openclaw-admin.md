# OpenClaw Administration Skill

Use when managing, configuring, troubleshooting, or deploying OpenClaw instances. Covers config schema, CLI commands, gateway management, security, workspace files, heartbeat, channels, skills, and common pitfalls.

IMPORTANT: NEVER guess config values. If unsure of a valid value, consult this reference FIRST. Invalid config keys cause the gateway to refuse to start entirely (strict Zod schema validation).

---

## Config File: `~/.openclaw/openclaw.json`

Format: JSON5 (comments, trailing commas, unquoted keys allowed). Unknown keys = gateway refuses to start. Only exception: `$schema` at root.

CRITICAL: Never edit config while gateway runs. Stop gateway first, edit, then start. The gateway's in-memory state can overwrite your changes.

---

## Config Schema: Valid Values Reference

### gateway

| Key | Valid Values | Default | Restart Required |
|-----|-------------|---------|-----------------|
| `gateway.port` | number | `18789` | Yes |
| `gateway.bind` | `"loopback"`, `"lan"`, `"tailnet"`, `"custom"`, `"auto"` | `"loopback"` | Yes |
| `gateway.mode` | `"local"`, `"remote"` | - | Yes |
| `gateway.auth.mode` | `"token"`, `"password"`, `"trusted-proxy"` | - | Yes |
| `gateway.auth.token` | hex string | - | Yes |
| `gateway.auth.allowTailscale` | boolean | - | Yes |
| `gateway.reload.mode` | `"hybrid"`, `"hot"`, `"restart"`, `"off"` | `"hybrid"` | Yes |
| `gateway.controlUi.dangerouslyDisableDeviceAuth` | boolean | `false` | - |
| `gateway.controlUi.allowInsecureAuth` | boolean | `false` | - |
| `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback` | boolean | `false` | - |

### agents.defaults

| Key | Valid Values | Default |
|-----|-------------|---------|
| `model.primary` | `"provider/model-id"` | - |
| `model.fallbacks` | string[] | - |
| `maxConcurrent` | number | `4` |
| `timeoutSeconds` | number | `600` |
| `subagents.model` | string | - |
| `subagents.maxConcurrent` | number | `8` |

### agents.defaults.sandbox

| Key | Valid Values | Default |
|-----|-------------|---------|
| `mode` | `"off"`, `"non-main"`, `"all"` | `"non-main"` |
| `scope` | `"session"`, `"agent"`, `"shared"` | `"session"` |
| `workspaceAccess` | `"none"`, `"ro"`, `"rw"` | `"none"` |
| `docker.network` | `"none"`, etc. | `"none"` |

### agents.defaults.heartbeat

| Key | Valid Values | Default |
|-----|-------------|---------|
| `every` | duration string: `"30m"`, `"1h"`, `"4h"`, `"0m"` (disable) | `"30m"` |
| `target` | `"none"`, `"last"`, channel name (`"telegram"`, `"discord"`, etc.) | `"none"` |
| `model` | `"provider/model-id"` | agent's default |
| `lightContext` | boolean | `false` |
| `directPolicy` | `"allow"`, `"block"` | `"allow"` |
| `ackMaxChars` | number | `300` |
| `showOk` | boolean | `false` |
| `showAlerts` | boolean | `true` |
| `activeHours.start` | `"HH:MM"` | - |
| `activeHours.end` | `"HH:MM"` | - |
| `activeHours.timezone` | IANA tz, `"user"`, `"local"` | - |
| `prompt` | string | default heartbeat prompt |
| `includeReasoning` | boolean | `false` |
| `session` | `"main"` or explicit key | `"main"` |

### agents.defaults.compaction

| Key | Valid Values | Default |
|-----|-------------|---------|
| `mode` | `"safeguard"`, `"aggressive"` | `"safeguard"` |
| `reserveTokensFloor` | number | `20000` |
| `identifierPolicy` | `"strict"`, `"off"`, `"custom"` | `"strict"` |
| `memoryFlush.enabled` | boolean | - |
| `memoryFlush.softThresholdTokens` | number | `4000` |

### tools

| Key | Valid Values | Default |
|-----|-------------|---------|
| `profile` | `"minimal"`, `"coding"`, `"messaging"`, `"full"` | - |
| `allow` | string[] (tool names, `"group:*"`) | `[]` |
| `deny` | string[] (tool names, `"group:*"`) | `[]` |
| `elevated.enabled` | boolean | `false` |

### tools.exec — CRITICAL: Know these values

| Key | Valid Values | Default |
|-----|-------------|---------|
| `security` | **`"deny"`, `"allowlist"`, `"full"`** | - |
| `ask` | `"off"`, `"on-miss"`, `"always"` | - |
| `askFallback` | `"deny"`, `"allowlist"`, `"full"` | `"deny"` |
| `host` | `"gateway"`, `"sandbox"` | - |
| `timeout` | number (seconds) | `1800` |

NEVER use `"open"` for exec.security. The valid values are ONLY: `"deny"`, `"allowlist"`, `"full"`.

### tools.fs

| Key | Valid Values |
|-----|-------------|
| `workspaceOnly` | boolean |

### session

| Key | Valid Values | Default |
|-----|-------------|---------|
| `dmScope` | `"main"`, `"per-peer"`, `"per-channel-peer"`, `"per-account-channel-peer"` | `"main"` |
| `reset.mode` | `"daily"`, `"idle"`, `"weekdays"`, `"never"` | - |

### channels (per-channel)

| Key | Valid Values |
|-----|-------------|
| `dmPolicy` | `"pairing"`, `"allowlist"`, `"open"`, `"disabled"` |
| `groupPolicy` | `"allowlist"`, `"open"`, `"disabled"` |
| `streamMode` | `"off"`, `"partial"`, `"block"`, `"progress"` |

### browser

| Key | Valid Values |
|-----|-------------|
| `ssrfPolicy.dangerouslyAllowPrivateNetwork` | boolean (ALWAYS set `false` in production) |

### discovery

| Key | Valid Values |
|-----|-------------|
| `mdns.mode` | `"off"`, `"minimal"`, `"full"` |

### logging

| Key | Valid Values |
|-----|-------------|
| `level` | `"debug"`, `"info"`, `"warn"`, `"error"` |
| `redactSensitive` | `"tools"` etc. |

### update

| Key | Valid Values |
|-----|-------------|
| `channel` | `"stable"`, `"beta"`, `"dev"` |
| `auto.enabled` | boolean |
| `auto.stableDelayHours` | number |

---

## Tool Groups Reference

| Group | Tools |
|-------|-------|
| `group:runtime` | exec, bash, process |
| `group:fs` | read, write, edit, apply_patch |
| `group:sessions` | session management |
| `group:memory` | memory_search, memory_get |
| `group:web` | web_search, web_fetch |
| `group:ui` | browser, canvas |
| `group:automation` | cron, gateway |
| `group:messaging` | message |
| `group:nodes` | nodes |

Tool profiles expand to: `"minimal"` = session_status only. `"coding"` = fs+runtime+sessions+memory+image. `"messaging"` = messaging+sessions. `"full"` = no restriction.

---

## CLI Commands Quick Reference

### Diagnostics
```
openclaw doctor [--fix] [--deep] [--non-interactive] [--generate-gateway-token]
openclaw security audit [--deep] [--fix] [--json]
openclaw status [--all] [--deep]
openclaw health [--json] [--verbose]
openclaw logs [--follow] [--json] [--limit N]
```

### Gateway
```
openclaw gateway install [--force]
openclaw gateway start|stop|restart
openclaw gateway status [--deep]
```

### Config
```
openclaw config get <path>
openclaw config set <path> <value>
openclaw config unset <path>
openclaw config validate
```

### Channels
```
openclaw channels list|add|remove|status|login|logout|logs
openclaw channels status --probe [--all]
```

### Models
```
openclaw models list [--all] [--provider <name>]
openclaw models set <provider/model>
openclaw models status
openclaw models scan
openclaw models aliases add <alias> <provider/model>
openclaw models fallbacks add|remove|list|clear
```

### Agents
```
openclaw agents list [--bindings]
openclaw agents add|delete <name>
openclaw agents bind --agent <name> --bind <channel:target>
```

### Skills
```
openclaw skills list [--eligible]
openclaw skills info <name>
openclaw skills check
```

### Memory
```
openclaw memory status [--deep] [--index]
openclaw memory index [--all] [--verbose]
openclaw memory search "query"
```

### Cron
```
openclaw cron list|add|edit|run|enable|disable|remove|status
openclaw cron runs <jobId>
```

### Secrets
```
openclaw secrets audit|configure|apply|reload
```

### Update
```
openclaw update [--dry-run] [--channel stable|beta|dev]
```

### Manual Heartbeat
```
openclaw system event --text "Check for urgent follow-ups" --mode now
```

---

## Workspace Files (`~/.openclaw/workspace/`)

| File | Purpose | Key Notes |
|------|---------|-----------|
| `SOUL.md` | Persona, tone, values, boundaries | 50-150 lines. 80% of agent behavior. Use absolutes ("NEVER", "ALWAYS"). |
| `AGENTS.md` | Operating instructions, safety rules | Priorities, workflows, memory usage. The operating manual. |
| `IDENTITY.md` | Structured persona card | Name, Creature, Vibe, Emoji, Avatar |
| `HEARTBEAT.md` | Scheduled task checklist | Markdown checklists. Keep small for token savings. |
| `USER.md` | User preferences | Name, timezone, communication preferences |
| `TOOLS.md` | Environment notes | SSH hosts, device names, etc. Guidance only, doesn't control tool access. |
| `MEMORY.md` | Long-term curated facts | Private sessions only. Keep curated and small. |
| `memory/YYYY-MM-DD.md` | Daily logs | Ephemeral. Today + yesterday loaded at session start. |

All workspace files capped at 20,000 chars each, 150,000 chars total. NEVER put credentials in workspace files.

---

## Heartbeat Best Practices

- Use `lightContext: true` to only inject HEARTBEAT.md (not full workspace) — saves tokens
- Set `activeHours` to avoid firing while user sleeps
- Use a cheap model override for heartbeat (`model: "anthropic/claude-haiku-3"`)
- Empty HEARTBEAT.md (only blank lines/headers) = heartbeat run skipped entirely
- `HEARTBEAT_OK` response = nothing needs attention, message suppressed by default
- If all three visibility flags (`showOk`, `showAlerts`, `useIndicator`) are false, heartbeat is skipped

### Known Issues
- Per-agent intervals may be ignored (all fire on main schedule) — Issue #14986
- Timer may stop after first batch — Issue #31139
- Heartbeat model override may not work — Issue #9556

---

## Discord Setup Checklist

1. Create app at Discord Developer Portal
2. Enable **Message Content Intent** and **Server Members Intent** on Bot page
3. Copy Bot Token
4. Configure in `openclaw.json`:
```json5
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "BOT_TOKEN",
      "groupPolicy": "allowlist",
      "guilds": {
        "GUILD_ID": {
          "requireMention": true,
          "users": ["USER_ID"]
        }
      }
    }
  }
}
```
5. Error 4014 = forgot Message Content Intent

---

## Security Checklist

- `gateway.auth.mode: "token"` — NEVER run without auth
- `gateway.bind: "loopback"` — or use Tailscale/SSH tunnel
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: false`
- All `dangerously*` flags = `false`
- `session.dmScope: "per-channel-peer"` for multi-user
- File permissions: `~/.openclaw/` = 700, config/env = 600
- Credentials in `.env` file (chmod 600), loaded via systemd EnvironmentFile
- Audit skills before installing from ClawHub (supply-chain attacks documented)
- `redactSensitive` only affects console display, NOT persisted session transcripts

---

## Common Pitfalls — NEVER Repeat These

1. **Invalid exec.security value**: Only `"deny"`, `"allowlist"`, `"full"`. NOT "open", "unrestricted", "none".
2. **Editing config while gateway runs**: In-memory state overwrites your changes. Stop first.
3. **heartbeat.every as number**: Must be a string like `"4h"`, not `4`.
4. **gateway.bind raw addresses**: Use `"loopback"`, `"lan"`, `"tailnet"` — NOT `"0.0.0.0"` or `"localhost"`.
5. **Per-agent overrides silently ignored**: Some keys only work at `agents.defaults` level.
6. **Cron jobs don't pick up config changes**: Must recreate cron jobs after config changes.
7. **Gateway takes ~40s to start**: Don't kill and restart too quickly.
8. **Model stored in 4 places**: main config, session state, cron payloads, model allowlist. Must update all.
9. **After upgrades**: Always run `openclaw doctor --fix` then `openclaw gateway restart`.
10. **Bun not supported**: Use Node.js 22+ only for gateway runtime.

---

## Skill Development Reference

Skills live in directories with a `SKILL.md` file (YAML frontmatter + markdown body).

### Locations (highest priority wins)
1. `<workspace>/skills/` — workspace-level overrides
2. `~/.openclaw/skills/` — managed/shared skills
3. Bundled skills — ship with OpenClaw

### SKILL.md Frontmatter
```yaml
---
name: my-skill
description: "Clear trigger description — this is the routing signal"
user-invocable: true
allowed-tools: ["bash", "read", "write"]
---
```

### Key Fields
| Field | Purpose |
|-------|---------|
| `name` | Unique identifier (lowercase, hyphens) |
| `description` | Routing signal for semantic matching — NOT marketing copy |
| `user-invocable` | Whether users can trigger via slash command |
| `disable-model-invocation` | Prevents autonomous model selection |
| `allowed-tools` | Permitted tools for this skill |
| `metadata` | JSON gating (requires.bins, requires.env, os filtering) |

### Body Sections
1. What it does
2. Inputs needed
3. Step-by-step workflow
4. Guardrails / safety constraints
5. Failure handling / escalation paths

Keep under 500 lines. Move details to `references/` subdirectory.

### ClawHub (Marketplace)
```
clawhub search "keyword"    # Semantic search
clawhub install <slug>      # Install
clawhub update --all        # Update all
```

WARNING: 341+ malicious skills documented on ClawHub. Always audit source before installing.

---

## Operational Runbook

### Config Change Workflow
1. `systemctl --user stop openclaw-gateway` (or `openclaw gateway stop`)
2. Edit `~/.openclaw/openclaw.json`
3. `openclaw config validate` (or `openclaw doctor`)
4. `systemctl --user start openclaw-gateway` (or `openclaw gateway start`)
5. Verify: `systemctl --user is-active openclaw-gateway`

### Troubleshooting Sequence
1. `openclaw gateway status` — is it running?
2. `openclaw doctor` — config valid?
3. `journalctl --user -u openclaw-gateway -n 50` — what do logs say?
4. `openclaw channels status --probe` — channels connected?
5. `openclaw security audit --deep` — security posture?

### Post-Upgrade Checklist
1. `openclaw doctor --fix`
2. `openclaw gateway restart`
3. `openclaw health`
4. Check channels: `openclaw channels status --probe --all`
5. Recreate any cron jobs if config changed
