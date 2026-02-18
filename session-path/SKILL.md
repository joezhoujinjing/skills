---
name: session-path
description: Print the file path to the current conversation's session file (Cursor agent-transcript, Claude Code/Codex JSONL).
---

Require an agent parameter: `cursor`, `claude`, or `codex`.

- If the user ran `/session-path` with no parameter, ask: **"Which agent? (cursor, claude, or codex)"** and do not run the command until they specify one.
- When the agent is specified (from the invocation or their reply), run the script below using the Bash tool, passing the agent name as the argument.

For Cursor: always use the most recently modified transcript file (do not use `CLAUDE_SESSION_ID` or `CURSOR_SPAWNED_BY_EXTENSION_ID`).

Run: `bash ~/.claude/skills/session-path/session-path.sh <agent>`

Print the resulting session file path to the user and nothing else.
