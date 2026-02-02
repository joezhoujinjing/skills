#!/usr/bin/env python3
"""Export Jarvis cookies to notebooklm-mcp format."""
import json
import pickle
import time
from pathlib import Path

JARVIS_COOKIES = Path.home() / ".jarvis" / "cookies.dat"
MCP_AUTH = Path.home() / ".notebooklm-mcp-cli" / "auth.json"

# Load cookies
with open(JARVIS_COOKIES, "rb") as f:
    cookies = pickle.load(f)

# Filter Google cookies
google_cookies = {}
for c in cookies:
    domain = getattr(c, 'domain', '') or c.get('domain', '')
    if 'google.com' in domain:
        name = getattr(c, 'name', '') or c.get('name', '')
        value = getattr(c, 'value', '') or c.get('value', '')
        google_cookies[name] = value

# Export
MCP_AUTH.parent.mkdir(parents=True, exist_ok=True)
MCP_AUTH.write_text(json.dumps({
    "cookies": google_cookies,
    "csrf_token": "",
    "session_id": "",
    "extracted_at": time.time()
}, indent=2))

print(f"✓ Exported {len(google_cookies)} cookies to {MCP_AUTH}")
print("Ready for notebooklm-mcp!")
