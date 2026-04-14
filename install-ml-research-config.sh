#!/usr/bin/env bash
# =============================================================================
# install-ml-research-config.sh
# Installs ML research CLAUDE.md and agent config into the ClaudeCode repo.
# Run from the root of your cloned NCMFN/ClaudeCode repository.
# =============================================================================

set -e

REPO_ROOT="$(pwd)"
AGENT_DIR="$REPO_ROOT/.claude/agents"
CONTEXT_DIR="$REPO_ROOT/contexts"

echo ""
echo "=== ML Research Config Installer ==="
echo "Repo root: $REPO_ROOT"
echo ""

# --- 1. CLAUDE.md at repo root ---
if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
  echo "[!] CLAUDE.md already exists. Creating CLAUDE-ml-research.md instead."
  cp CLAUDE.md "$REPO_ROOT/CLAUDE-ml-research.md"
  echo "[NOTE] Merge CLAUDE-ml-research.md into your existing CLAUDE.md manually."
else
  cp CLAUDE.md "$REPO_ROOT/CLAUDE.md"
  echo "[OK] CLAUDE.md written to repo root."
fi

# --- 2. Agent definition ---
mkdir -p "$AGENT_DIR"
cp .claude/agents/ml-research-agent.md "$AGENT_DIR/ml-research-agent.md"
echo "[OK] ml-research-agent.md written to $AGENT_DIR/"

# --- 3. Research context ---
mkdir -p "$CONTEXT_DIR"
cp contexts/research.md "$CONTEXT_DIR/research.md"
echo "[OK] research.md written to $CONTEXT_DIR/"

# --- 4. Outputs directory ---
mkdir -p "$REPO_ROOT/outputs"
echo "[OK] /outputs/ directory created."

echo ""
echo "=== Installation complete ==="
echo ""
echo "Next steps:"
echo "  1. Open Claude Code in this repo:  claude"
echo "  2. To run an ML task, provide:"
echo "       Dataset : <URL or file path>"
echo "       Task    : <prediction goal>"
echo "       Target  : <column name>"
echo "  3. Invoke the agent with:  @ml-research-agent"
echo ""
