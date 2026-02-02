---
name: ai-browser
description: "Jarvis browser profile manager for AI agent automation. Wraps ai-dev-browser to provide persistent login sessions and cookie export for notebooklm-mcp. Use when you need to: (1) Set up persistent browser sessions for AI agents, (2) Login to websites and save cookies, (3) Export authentication for notebooklm-mcp, (4) Automate basic browser tasks."
---

# AI Browser

Manages Jarvis browser profile (`~/.jarvis`) for AI agent automation. Built on ai-dev-browser.

## Setup

```bash
source tools/jarvis.sh
jarvis_setup
```

## Core Usage

```bash
# Start browser and login
jarvis_start --url https://notebooklm.google.com
# Login manually, then save cookies
jarvis_cookies_save
jarvis_cookies_export_mcp

# Basic automation
jarvis_goto --url https://example.com
jarvis_screenshot /tmp/page.png
jarvis_click --selector "#button"
```

## Key Commands

- `jarvis_start` - Start browser with Jarvis profile
- `jarvis_cookies_save` - Save cookies from current session
- `jarvis_cookies_export_mcp` - Export for notebooklm-mcp
- `jarvis_goto --url <url>` - Navigate
- `jarvis_screenshot <file>` - Screenshot
- `jarvis_click --selector <sel>` - Click element

## Integration

Export cookies for notebooklm-mcp to share auth across tools:

```bash
jarvis_start --url https://notebooklm.google.com
# Login in browser
jarvis_cookies_save
jarvis_cookies_export_mcp
# Now notebooklm-http-skill can use the auth
```

All ai-dev-browser tools available via `jarvis_*` prefix. Use `jarvis_help` or run any tool with `--help`.
