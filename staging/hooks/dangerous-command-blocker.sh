#!/bin/bash
# Dangerous command blocker — runs as PreToolUse hook
# More reliable than deny rules (works regardless of permission mode)
# Exit 2 = block, Exit 0 = allow

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name // ""' 2>/dev/null)

# Fail-closed: if we cannot determine the tool name (malformed JSON, jq error),
# block the call rather than allowing it through
if [ -z "$tool_name" ]; then
  echo "[Hook] BLOCKED: Unable to parse tool input (fail-closed)" >&2
  exit 2
fi

# Only inspect Bash tool calls; other tools pass through
[ "$tool_name" != "Bash" ] && exit 0

# Fail-closed: if this is a Bash call but we cannot extract the command, block it
cmd=$(echo "$input" | jq -r '.tool_input.command // ""')
if [ -z "$cmd" ]; then
  echo "[Hook] BLOCKED: Bash tool with empty command (fail-closed)" >&2
  exit 2
fi

blocked() {
  echo "[Hook] BLOCKED: $1" >&2
  echo "[Hook] $2" >&2
  exit 2
}

# --- RECURSIVE RM (all flag combinations) ---
# Catches: rm -r, rm -rf, rm -fr, rm -Rf, rm -RF, rm -v -r, rm --recursive
if echo "$cmd" | grep -qE '\brm\s+(-[a-zA-Z]+\s+)*-[a-zA-Z]*[rR][a-zA-Z]*(\s|$)'; then
  blocked "Recursive rm detected" "Use 'trash' instead of rm -r"
fi
if echo "$cmd" | grep -qE '\brm\s+.*--recursive'; then
  blocked "Recursive rm detected" "Use 'trash' instead of rm --recursive"
fi

# --- SUDO (local only — SSH sudo handled by ssh-tier-gate.sh) ---
# Skip if this is an SSH command; the tiered SSH hook classifies remote sudo
if ! echo "$cmd" | grep -qE '^\s*ssh\s'; then
  if echo "$cmd" | grep -qE '(^|;|&&|\|)\s*sudo\s'; then
    blocked "sudo is not allowed" "Ask the user to run privileged commands manually"
  fi
fi

# --- DD EVASION (absolute paths, backslash, command prefix) ---
if echo "$cmd" | grep -qE '(^|;|&&|\|)\s*(\\\\|/usr/bin/|/bin/|command\s+)dd\s'; then
  blocked "dd via path/evasion detected" "dd disk writes are not allowed"
fi

# --- PIPE-TO-SHELL BYPASS (process substitution) ---
if echo "$cmd" | grep -qE '(bash|sh|zsh)\s+<\('; then
  blocked "Process substitution to shell" "Download the script, review it, then run it"
fi
if echo "$cmd" | grep -qE '(source|\.\s)\s*<\('; then
  blocked "Source with process substitution" "Download the script, review it, then run it"
fi

# --- EVAL WITH REMOTE FETCH ---
if echo "$cmd" | grep -qE 'eval\s.*\$\(.*(curl|wget)'; then
  blocked "eval with remote fetch" "Download the script, review it, then run it"
fi

# --- DOWNLOAD-THEN-EXECUTE ---
if echo "$cmd" | grep -qE '(curl|wget)\s.*&&\s*(bash|sh|zsh|chmod\s+\+x)\s'; then
  blocked "Download-then-execute pattern" "Download the script, review it, then run it"
fi

# --- GIT DESTRUCTIVE OPS ---
if echo "$cmd" | grep -qE '\bgit\s+clean\s+.*-[a-zA-Z]*f'; then
  blocked "git clean with force" "This deletes untracked files permanently"
fi
if echo "$cmd" | grep -qE '\bgit\s+(checkout|restore)\s+\.\s*(;|&&|\||$)'; then
  blocked "Discarding all working tree changes" "This is irreversible for unstaged changes"
fi
if echo "$cmd" | grep -qE '\bgit\s+push\s.*--mirror'; then
  blocked "git push --mirror" "This overwrites the entire remote"
fi

# --- GIT HISTORY DESTRUCTION (recovery path elimination) ---
if echo "$cmd" | grep -qE '\bgit\s+reflog\s+expire\b'; then
  blocked "git reflog expire" "This removes recovery points — you lose the ability to undo"
fi
if echo "$cmd" | grep -qE '\bgit\s+filter-branch\b'; then
  blocked "git filter-branch" "This destructively rewrites history — use git filter-repo instead"
fi
if echo "$cmd" | grep -qE '(^|;|&&|\|)\s*git\s+prune\b'; then
  blocked "git prune" "This permanently removes unreachable objects"
fi

# --- DOCKER DESTRUCTIVE OPS ---
if echo "$cmd" | grep -qE '\bdocker\s+system\s+prune'; then
  blocked "docker system prune" "This removes all unused containers, images, and networks"
fi
if echo "$cmd" | grep -qE '\bdocker\s+volume\s+(rm|remove|prune)'; then
  blocked "docker volume destruction" "This permanently deletes persistent data"
fi

# --- DOCKER SERVICE/STACK/NETWORK DESTRUCTION ---
if echo "$cmd" | grep -qE '\bdocker\s+(service|stack)\s+(rm|remove)\b'; then
  blocked "docker service/stack removal" "This tears down running services and their state"
fi
if echo "$cmd" | grep -qE '\bdocker\s+network\s+(rm|remove|prune)\b'; then
  blocked "docker network removal" "This can disconnect running containers"
fi
if echo "$cmd" | grep -qE '\bdocker[ -]compose\s+down\s+.*(-v\b|--volumes\b)'; then
  blocked "docker compose down with volume deletion" "The -v/--volumes flag deletes attached volumes and their data"
fi

# --- CLOUD INFRASTRUCTURE: GCLOUD ---
if echo "$cmd" | grep -qE '\bgcloud\s+.*\bdelete\b'; then
  blocked "gcloud delete operation" "Cloud resource deletion requires explicit user approval — run manually"
fi
if echo "$cmd" | grep -qE '\bgcloud\s+storage\s+rm\b'; then
  blocked "gcloud storage deletion" "Cloud Storage deletion requires explicit user approval — run manually"
fi

# --- CLOUD INFRASTRUCTURE: AWS CLI ---
if echo "$cmd" | grep -qE '\baws\s+\S+\s+(delete|terminate)\b'; then
  blocked "AWS destructive operation" "AWS resource deletion/termination requires explicit user approval — run manually"
fi
if echo "$cmd" | grep -qE '\baws\s+s3\s+(rm|rb)\b'; then
  blocked "AWS S3 deletion" "S3 object/bucket deletion requires explicit user approval — run manually"
fi

# --- CLOUD INFRASTRUCTURE: TERRAFORM / CDK ---
if echo "$cmd" | grep -qE '\bterraform\s+(destroy|taint|untaint)\b'; then
  blocked "Terraform destructive operation" "Infrastructure teardown requires explicit user approval — run manually"
fi
if echo "$cmd" | grep -qE '\bterraform\s+apply\s+.*-auto-approve'; then
  blocked "Terraform auto-approve" "Never auto-approve infrastructure changes — review the plan first"
fi
if echo "$cmd" | grep -qE '\bterraform\s+state\s+rm\b'; then
  blocked "Terraform state removal" "Removing resources from state causes drift and orphaned infrastructure"
fi
if echo "$cmd" | grep -qE '\bcdk\s+destroy\b'; then
  blocked "CDK destroy" "Infrastructure teardown requires explicit user approval — run manually"
fi

# --- SSH REMOTE COMMANDS ---
# Full SSH command classification is handled by ssh-tier-gate.sh (tiered system)
# This blocker only catches SSH commands if the tier gate hook is somehow missing
if ! [ -x "$HOME/.claude/hooks/ssh-tier-gate.sh" ]; then
  if echo "$cmd" | grep -qE '\bssh\s+.*\b(dd\s+if=|mkfs|wipefs|shutdown|reboot|poweroff|halt|init\s+[06])'; then
    blocked "Destructive command via SSH" "Remote destructive operations require explicit user approval — run manually"
  fi
fi

# --- CREDENTIAL FILE TRANSFER ---
if echo "$cmd" | grep -qE '\b(scp|rsync)\s+.*\.(env|pem|key|p12|jks)\b'; then
  blocked "Credential file transfer" "NEVER transfer credential files to remote servers — use env vars in orchestrator"
fi
if echo "$cmd" | grep -qE '\b(scp|rsync)\s+.*(id_rsa|id_ed25519|id_ecdsa|id_dsa|\.aws/credentials)\b'; then
  blocked "SSH/cloud credential transfer" "NEVER transfer private keys or cloud credentials to remote servers"
fi

# --- SECRET LEAKAGE ---
if echo "$cmd" | grep -qE '\bcat\s+.*(/(id_rsa|id_ed25519|id_ecdsa|id_dsa))\b'; then
  blocked "Reading SSH private key" "Private keys should never be read or displayed via bash"
fi
if echo "$cmd" | grep -qE '\bcat\s+.*\.aws/(credentials|config)\b'; then
  blocked "Reading AWS credentials" "Cloud credentials should never be displayed in terminal"
fi
if echo "$cmd" | grep -qiE '\bhistory\s*\|\s*grep\s+.*(password|token|secret|api.key|credential)\b'; then
  blocked "Searching history for secrets" "This can leak credentials from command history"
fi

# --- FILE DESTRUCTION ---
if echo "$cmd" | grep -qE '(^|;|&&|\|)\s*(truncate|shred|wipe|srm)\s'; then
  blocked "File destruction command" "Use 'trash' for safe deletion"
fi

# --- DISK FORMATTING (mkfs variants) ---
if echo "$cmd" | grep -qE '(^|;|&&|\|)\s*(mkfs|mke2fs|newfs|wipefs)\b'; then
  blocked "Filesystem formatting command" "This destroys disk data"
fi

# --- DATABASE DROPS ---
if echo "$cmd" | grep -qiE "(DROP\s+(TABLE|DATABASE|SCHEMA)|TRUNCATE\s+|FLUSHALL|FLUSHDB|dropDatabase)"; then
  blocked "Database destruction command" "This permanently deletes data"
fi

exit 0
