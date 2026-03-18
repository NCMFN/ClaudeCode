---
paths:
  - "**/*.html"
  - "**/*.css"
  - "**/*.js"
---
# Vanilla JavaScript/CSS/HTML Hooks

> This file extends [common/hooks.md](../common/hooks.md) with vanilla HTML/CSS/JavaScript specific content.

## PostToolUse Hooks

Configure in `~/.claude/settings.json`:

- **Prettier**: Auto-format `.html`, `.css`, and `.js` files after every edit
- **ESLint**: Run ESLint on edited `.js` files to catch errors and style violations
- **console.log warning**: Warn when `console.log` is found in edited `.js` files

## Stop Hooks

- **console.log audit**: Scan all modified `.js` files for `console.log` before session ends and report any found

## Example Hook Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "prettier --write \"$CLAUDE_TOOL_INPUT_FILE_PATH\" 2>/dev/null || true",
            "description": "Auto-format HTML/CSS/JS with Prettier"
          },
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_INPUT_FILE_PATH\" == *.js ]]; then npx eslint --fix \"$CLAUDE_TOOL_INPUT_FILE_PATH\" 2>/dev/null || true; fi",
            "description": "ESLint fix on JS files"
          },
          {
            "type": "command",
            "command": "if [[ \"$CLAUDE_TOOL_INPUT_FILE_PATH\" == *.js ]] && grep -q 'console\\.log' \"$CLAUDE_TOOL_INPUT_FILE_PATH\" 2>/dev/null; then echo \"WARNING: console.log found in $CLAUDE_TOOL_INPUT_FILE_PATH\"; fi",
            "description": "Warn on console.log in JS files"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "git diff --name-only HEAD 2>/dev/null | grep '\\.js$' | xargs grep -l 'console\\.log' 2>/dev/null | while read f; do echo \"console.log audit: $f\"; done || true",
            "description": "Audit modified JS files for console.log before session ends"
          }
        ]
      }
    ]
  }
}
```
