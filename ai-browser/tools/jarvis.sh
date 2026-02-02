#!/usr/bin/env bash
# Jarvis Browser - Wrapper for ai-dev-browser with Jarvis profile

JARVIS_DIR="${HOME}/.jarvis"
PORT=9222

# Find Python with ai-dev-browser
if command -v python3.13 &>/dev/null && python3.13 -c "import ai_dev_browser" 2>/dev/null; then
    PY=python3.13
elif [ -f ~/.pyenv/versions/3.13.9/bin/python3 ]; then
    PY=~/.pyenv/versions/3.13.9/bin/python3
else
    PY=python3
fi

mkdir -p "$JARVIS_DIR"

# Core wrapper
_run() {
    "$PY" -m "ai_dev_browser.tools.$1" --port "$PORT" "${@:2}"
}

# Browser control
jarvis_start() { _run browser_start "$@"; }
jarvis_stop() { _run browser_stop "$@"; }

# Navigation
jarvis_goto() { _run page_goto "$@"; }
jarvis_reload() { _run page_reload "$@"; }

# Interaction
jarvis_click() { _run element_click "$@"; }
jarvis_type() { _run element_type "$@"; }

# Inspection
jarvis_screenshot() { _run page_screenshot "$@"; }
jarvis_html() { _run page_html "$@"; }
jarvis_eval() { _run page_eval "$@"; }

# Cookies
jarvis_cookies_save() { _run cookies_save "$@"; }
jarvis_cookies_load() { _run cookies_load "$@"; }

jarvis_cookies_export_mcp() {
    "$PY" "$(dirname "${BASH_SOURCE[0]}")/../scripts/export_cookies_mcp.py"
}

# Setup
jarvis_setup() {
    "$PY" "$(dirname "${BASH_SOURCE[0]}")/../scripts/jarvis_setup.py"
}

# Help
jarvis_help() {
    cat <<'EOF'
Jarvis Browser - AI agent browser automation

Core Commands:
  jarvis_setup                  - Initialize Jarvis profile
  jarvis_start [--url URL]      - Start browser
  jarvis_stop                   - Stop browser
  jarvis_goto --url URL         - Navigate
  jarvis_click --selector SEL   - Click element
  jarvis_type TEXT --selector SEL - Type text
  jarvis_screenshot FILE        - Take screenshot
  jarvis_cookies_save           - Save cookies
  jarvis_cookies_export_mcp     - Export for notebooklm-mcp

All commands support --help for options.
For full tool list: ai-dev-browser has 44 tools via jarvis_* prefix.
EOF
}

export -f jarvis_start jarvis_stop jarvis_goto jarvis_reload
export -f jarvis_click jarvis_type jarvis_screenshot jarvis_html jarvis_eval
export -f jarvis_cookies_save jarvis_cookies_load jarvis_cookies_export_mcp
export -f jarvis_setup jarvis_help
