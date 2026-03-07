#!/bin/bash
# SSH command tier gate — classifies SSH commands into safety tiers
# Runs as PreToolUse hook on Bash tool calls
#
# Tier 0: Read-only, observational (allow silently)
# Tier 1: State-changing but recoverable (allow with explanation)
# Tier 2: Significant state change (ask user permission)
# Tier 3: Catastrophic/irreversible (hard block)
#
# Exit 0 = allow, Exit 2 = block
# stdout JSON with permissionDecision for Tier 2

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // ""' 2>/dev/null)

# Only inspect Bash tool calls
[ "$tool_name" != "Bash" ] && exit 0

cmd=$(echo "$input" | jq -r '.tool_input.command // ""')
[ -z "$cmd" ] && exit 0

# Only inspect SSH commands
if ! echo "$cmd" | grep -qE '^\s*ssh\s'; then
  exit 0
fi

# Extract the remote command portion
# Strip: ssh [flags] [user@]host <remote_command>
# SSH flags that take an argument: -b -c -D -E -e -F -I -i -J -L -l -m -O -o -p -Q -R -S -W -w
# We strip flag+arg pairs, then the hostname, leaving the remote command
remote_cmd=$(echo "$cmd" | sed -E '
  s/^\s*ssh\s+//
  s/^(-[bcDEeFIiJLlmOopQRSWw]\s+\S+\s+)*//
  s/^(-[^ bcDEeFIiJLlmOopQRSWw]+\s+)*//
  s/^\S+\s+//
  s/^['\''"]//
  s/['\''"]$//
')

# If no remote command extracted (interactive session), note it
if [ -z "$remote_cmd" ]; then
  echo "[SSH] Interactive session — all commands typed will be visible to the user" >&2
  exit 0
fi

# ============================================================
# TIER 3: CATASTROPHIC — hard block (exit 2)
# Operations that destroy the server or make it unreachable
# ============================================================

blocked() {
  echo "[SSH] BLOCKED: $1" >&2
  echo "[SSH] $2" >&2
  exit 2
}

# Server shutdown/reboot — if misconfigured, server won't come back
if echo "$remote_cmd" | grep -qiE '\b(shutdown|reboot|poweroff|halt)\b'; then
  blocked "Server shutdown/reboot" "If the server doesn't come back, you need console access to fix it"
fi
if echo "$remote_cmd" | grep -qE '\binit\s+[06]\b'; then
  blocked "Runlevel change (shutdown/reboot)" "Server will go offline"
fi

# Disk/filesystem destruction
if echo "$remote_cmd" | grep -qE '\bdd\s+if='; then
  blocked "Raw disk write (dd)" "This overwrites disk data directly"
fi
if echo "$remote_cmd" | grep -qE '\b(mkfs|mke2fs|wipefs)\b'; then
  blocked "Filesystem format/wipe" "This destroys all data on the target device"
fi

# Wide-scope recursive deletion — root or system directories
if echo "$remote_cmd" | grep -qE '\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*\s+|--recursive\s+)(/\s|/\*|/$|/home\b|/var\b|/etc\b|/usr\b|/opt\b|/root\b|/boot\b|/srv\b|/lib\b|/bin\b|/sbin\b|\~/)'; then
  blocked "Wide-scope deletion of system directory" "This would destroy critical server infrastructure"
fi

# Fork bomb
if echo "$remote_cmd" | grep -qE ':\(\)\{'; then
  blocked "Fork bomb detected" "This will crash the server"
fi

# Terraform/CDK destruction via SSH
if echo "$remote_cmd" | grep -qE '\b(terraform\s+destroy|cdk\s+destroy)\b'; then
  blocked "Infrastructure destruction" "Run terraform/cdk destructive commands manually"
fi

# Direct disk device writes via redirection
if echo "$remote_cmd" | grep -qE '>\s*/dev/(sd|hd|vd|nvme|xvd|loop)'; then
  blocked "Direct disk device write" "This overwrites raw disk data"
fi

# System account password changes
if echo "$remote_cmd" | grep -qE '\bpasswd\s+(root|ubuntu|admin|www-data|postgres|mysql)\b'; then
  blocked "System account password change" "Changing system passwords remotely is too risky"
fi

# Docker compose down with volume deletion (data loss)
if echo "$remote_cmd" | grep -qE '\bdocker[ -]compose\s+down\s+.*(-v\b|--volumes\b)'; then
  blocked "Docker compose down with volume deletion" "The -v/--volumes flag permanently deletes persistent data"
fi

# Docker system prune
if echo "$remote_cmd" | grep -qE '\bdocker\s+system\s+prune'; then
  blocked "Docker system prune" "This removes all unused containers, images, and networks"
fi

# ============================================================
# TIER 2: SIGNIFICANT STATE CHANGE — ask user permission
# Harder to reverse, worth confirming
# ============================================================

ask_permission() {
  echo "[SSH] Needs approval: $1" >&2
  echo '{"permissionDecision": "ask"}'
  exit 0
}

# New package installation
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(apt|apt-get)\s+install\b'; then
  ask_permission "Installing packages: $(echo "$remote_cmd" | grep -oE '(apt|apt-get)\s+install\s+\S+' | head -1)"
fi
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(yum|dnf|apk)\s+(install|add)\b'; then
  ask_permission "Installing packages"
fi

# Package removal
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(apt|apt-get)\s+(remove|purge)\b'; then
  ask_permission "Removing packages"
fi
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(yum|dnf|apk)\s+(remove|erase|del)\b'; then
  ask_permission "Removing packages"
fi

# Firewall changes
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(ufw|iptables|nftables|firewall-cmd)\s'; then
  ask_permission "Firewall rule change"
fi

# SSL/certificate operations
if echo "$remote_cmd" | grep -qE '\b(certbot|acme\.sh)\s'; then
  ask_permission "SSL certificate operation"
fi

# User/group management
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(adduser|useradd|usermod|deluser|userdel|groupadd|groupmod|groupdel)\b'; then
  ask_permission "User/group management"
fi

# File permission/ownership changes
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(chmod|chown)\s'; then
  ask_permission "File permission/ownership change"
fi

# Docker volume/network lifecycle
if echo "$remote_cmd" | grep -qE '\bdocker\s+volume\s+(create|rm|remove)\b'; then
  ask_permission "Docker volume operation"
fi
if echo "$remote_cmd" | grep -qE '\bdocker\s+network\s+(create|rm|remove)\b'; then
  ask_permission "Docker network operation"
fi

# Docker service/stack removal
if echo "$remote_cmd" | grep -qE '\bdocker\s+(service|stack)\s+(rm|remove)\b'; then
  ask_permission "Docker service/stack removal"
fi

# Database destructive operations
if echo "$remote_cmd" | grep -qiE '\b(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s)'; then
  ask_permission "Database destructive operation"
fi

# Database restore (overwrites existing data)
if echo "$remote_cmd" | grep -qE '\b(pg_restore|mongorestore)\b'; then
  ask_permission "Database restore (may overwrite data)"
fi
if echo "$remote_cmd" | grep -qE 'mysql.*<\s*\S+\.sql'; then
  ask_permission "MySQL import (may overwrite data)"
fi

# Systemd unit enable/disable/mask
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?systemctl\s+(enable|disable|mask|unmask)\s'; then
  ask_permission "Systemd unit state change"
fi

# Systemd unit file creation/modification
if echo "$remote_cmd" | grep -qE '(tee|cat\s*>).*\.service\b'; then
  ask_permission "Systemd unit file modification"
fi

# Recursive file deletion (non-system directories — system dirs caught in Tier 3)
if echo "$remote_cmd" | grep -qE '\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*\s+|--recursive\s+)'; then
  ask_permission "Recursive file deletion: $(echo "$remote_cmd" | grep -oE 'rm\s+\S+\s+\S+' | head -1)"
fi

# ============================================================
# TIER 1: STATE-CHANGING BUT RECOVERABLE — allow with note
# Normal DevOps operations, just log what's happening
# ============================================================

explain() {
  echo "[SSH] $1" >&2
  exit 0
}

# Docker compose lifecycle
if echo "$remote_cmd" | grep -qE '\bdocker[ -]compose\s+(up|down|restart|pull|build|start|stop)\b'; then
  explain "Docker Compose: $(echo "$remote_cmd" | grep -oE 'docker[ -]compose\s+\S+' | head -1)"
fi

# Docker container lifecycle
if echo "$remote_cmd" | grep -qE '\bdocker\s+(start|stop|restart|kill)\s'; then
  explain "Docker container: $(echo "$remote_cmd" | grep -oE 'docker\s+(start|stop|restart|kill)\s+\S+' | head -1)"
fi

# Docker exec (running commands inside containers)
if echo "$remote_cmd" | grep -qE '\bdocker\s+exec\s'; then
  explain "Docker exec: running command inside container"
fi

# Service control (start/stop/restart/reload)
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(systemctl|service)\s+(restart|start|stop|reload)\s'; then
  explain "Service: $(echo "$remote_cmd" | grep -oE '(systemctl|service)\s+(restart|start|stop|reload)\s+\S+' | head -1)"
fi

# Package updates (not new installs)
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?(apt|apt-get)\s+(update|upgrade|dist-upgrade)\b'; then
  explain "Package update: $(echo "$remote_cmd" | grep -oE '(apt|apt-get)\s+(update|upgrade|dist-upgrade)' | head -1)"
fi
if echo "$remote_cmd" | grep -qE '\b(sudo\s+)?apt\s+autoremove\b'; then
  explain "Removing orphaned dependencies"
fi

# Git operations on server
if echo "$remote_cmd" | grep -qE '\bgit\s+(pull|fetch|checkout|switch|merge|rebase)\b'; then
  explain "Git: $(echo "$remote_cmd" | grep -oE 'git\s+\S+' | head -1)"
fi

# Build commands
if echo "$remote_cmd" | grep -qE '\b(npm\s+run\s+build|yarn\s+build|pnpm\s+build|cargo\s+build)\b'; then
  explain "Build: $(echo "$remote_cmd" | grep -oE '(npm\s+run\s+build|yarn\s+build|pnpm\s+build|cargo\s+build)' | head -1)"
fi

# Dependency install on server
if echo "$remote_cmd" | grep -qE '\b(npm\s+(install|ci)|yarn\s+install|pnpm\s+install)\b'; then
  explain "Dependencies: $(echo "$remote_cmd" | grep -oE '(npm|yarn|pnpm)\s+(install|ci)' | head -1)"
fi

# Database migrations
if echo "$remote_cmd" | grep -qE '\b(prisma\s+migrate|drizzle-kit\s+(push|migrate)|sequelize.*migrate|knex\s+migrate|typeorm\s+migration:run)\b'; then
  explain "DB migration: $(echo "$remote_cmd" | grep -oE '(prisma|drizzle-kit|sequelize|knex|typeorm)\s+\S+' | head -1)"
fi

# Nginx/Caddy/Apache config test and reload
if echo "$remote_cmd" | grep -qE '\b(nginx\s+-[ts]|nginx\s+-s\s+reload|caddy\s+reload|apachectl\s+(graceful|configtest))\b'; then
  explain "Web server: config test/reload"
fi

# Cron management
if echo "$remote_cmd" | grep -qE '\bcrontab\b'; then
  explain "Cron job management"
fi

# File edits via sed/tee/heredoc
if echo "$remote_cmd" | grep -qE '\b(sed\s+-i|tee\s)'; then
  explain "Remote file edit"
fi

# Single file deletion (non-recursive)
if echo "$remote_cmd" | grep -qE '\brm\s+[^-]'; then
  explain "File deletion: $(echo "$remote_cmd" | grep -oE 'rm\s+\S+' | head -1)"
fi

# Database backup
if echo "$remote_cmd" | grep -qE '\b(pg_dump|mysqldump|mongodump)\b'; then
  explain "Database backup"
fi

# Any remaining sudo commands not caught above
if echo "$remote_cmd" | grep -qE '\bsudo\s'; then
  explain "Privileged: $(echo "$remote_cmd" | sed 's/.*sudo\s\+/sudo /' | head -c 80)"
fi

# ============================================================
# TIER 0: READ-ONLY — silent pass-through
# ls, cat, tail, docker ps, logs, status, df, free, etc.
# ============================================================
exit 0
