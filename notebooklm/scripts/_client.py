#!/usr/bin/env python3
"""Shared client initialization for NotebookLM scripts."""

import sys
from pathlib import Path

# Add vendored notebooklm-mcp-cli to Python path
SCRIPT_DIR = Path(__file__).parent
VENDOR_DIR = SCRIPT_DIR.parent / "vendor" / "notebooklm-mcp-cli" / "src"
sys.path.insert(0, str(VENDOR_DIR))

try:
    from notebooklm_tools.core.client import NotebookLMClient
    from notebooklm_tools.core.auth import load_cached_tokens
    from notebooklm_tools.core.errors import ClientAuthenticationError
except ImportError as e:
    print(f"Error importing notebooklm_tools: {e}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Make sure the submodule is initialized:", file=sys.stderr)
    print("  cd ~/.claude/skills/notebooklm", file=sys.stderr)
    print("  git submodule update --init --recursive", file=sys.stderr)
    sys.exit(1)


def get_client() -> NotebookLMClient:
    """Get authenticated NotebookLM client.

    Returns:
        NotebookLMClient instance

    Raises:
        SystemExit: If authentication fails
    """
    try:
        # Load cached tokens
        tokens = load_cached_tokens()

        if not tokens:
            print("Error: No authentication tokens found", file=sys.stderr)
            print("", file=sys.stderr)
            print("To authenticate:", file=sys.stderr)
            print("1. Use ai-browser skill to log in to NotebookLM", file=sys.stderr)
            print("2. Run: jarvis_cookies_export_mcp", file=sys.stderr)
            sys.exit(1)

        # Create client with cookies
        client = NotebookLMClient(
            cookies=tokens.cookies,
            csrf_token=tokens.csrf_token,
            session_id=tokens.session_id
        )
        return client

    except ClientAuthenticationError as e:
        print(f"Authentication error: {e}", file=sys.stderr)
        print("Try re-authenticating: jarvis_cookies_export_mcp", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing client: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
