---
name: notebooklm
description: "Direct NotebookLM API access using notebooklm_tools Python library. No MCP server required - uses vendored library via git submodule for standalone operation."
---

# NotebookLM Direct API Skill

Direct access to Google NotebookLM via the `notebooklm_tools` Python library. This skill makes HTTP requests directly to notebooklm.google.com with **zero MCP dependencies** - the library is vendored as a git submodule.

## Architecture

```
Claude Code
    ↓ (Bash tool → Python)
notebooklm_tools library (vendored via submodule)
    ↓ (Direct HTTP + cookies)
notebooklm.google.com (internal API)
```

**No MCP server, no external packages - completely self-contained!**

## Setup

### 1. Initialize the Submodule

```bash
cd ~/.claude/skills/notebooklm
git submodule update --init --recursive
```

### 2. Install Python Dependencies

The vendored library only requires `httpx`:

```bash
pip install httpx
```

### 3. Authentication Setup

Use the **ai-browser** skill to log in and export cookies:

```bash
# Start browser and log in to NotebookLM
source ~/.claude/skills/ai-browser/tools/jarvis.sh
jarvis_start --url https://notebooklm.google.com

# After logging in, save cookies
jarvis_cookies_save
jarvis_cookies_export_mcp
```

Cookies are stored in `~/.notebooklm-mcp-cli/auth.json` and automatically loaded by the scripts.

## Usage

### Quick Start with Bash Functions

```bash
# Source the bash wrapper
source ~/.claude/skills/notebooklm/tools/notebooklm.sh

# List notebooks
nb_list

# Create a notebook
nb_create "My Research"

# Add sources
nb_add_url <notebook_id> "https://arxiv.org/abs/2301.00001" --wait

# Query notebook
nb_query <notebook_id> "What are the main findings?"
```

### Direct Python Script Usage

```bash
cd ~/.claude/skills/notebooklm

# List all notebooks
python3 scripts/list_notebooks.py

# Create notebook
python3 scripts/create_notebook.py --title "AI Research"

# Add URL source
python3 scripts/add_source.py <notebook_id> --url "https://example.com" --wait

# Add text source
python3 scripts/add_source.py <notebook_id> --text "Content here" --title "My Notes"

# List sources
python3 scripts/list_sources.py <notebook_id>

# Query notebook
python3 scripts/query.py <notebook_id> --question "What are the key points?"
```

## Available Scripts

### Notebook Management

- `list_notebooks.py` - List all notebooks
- `create_notebook.py --title <title>` - Create new notebook
- `query.py <notebook_id> --question <question>` - Ask a question

### Source Management

- `add_source.py <notebook_id> --url <url>` - Add URL/YouTube source
- `add_source.py <notebook_id> --text <text> --title <title>` - Add text source
- `add_source.py <notebook_id> --file <path>` - Upload local file
- `list_sources.py <notebook_id>` - List all sources

### Options

- `--json` - Output as JSON
- `--wait` - Wait for source processing to complete (for add_source)

## Direct API Usage in Python

You can also use the library directly in your own Python scripts:

```python
import sys
from pathlib import Path

# Add vendored library to path
vendor_path = Path.home() / ".claude/skills/notebooklm/vendor/notebooklm-mcp-cli/src"
sys.path.insert(0, str(vendor_path))

from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

# Get authenticated client
tokens = load_cached_tokens()
client = NotebookLMClient(
    cookies=tokens.cookies,
    csrf_token=tokens.csrf_token,
    session_id=tokens.session_id
)

# List notebooks
notebooks = client.list_notebooks()
for nb in notebooks:
    print(f"{nb.title}: {nb.id}")

# Create notebook
new_nb = client.create_notebook("My Research")

# Add source
client.add_url_source(new_nb.id, "https://example.com", "Example Site")

# Query
result = client.query(new_nb.id, "What is this about?")
print(result)

# Clean up
client.close()
```

## API Reference

The vendored `notebooklm_tools.core.client.NotebookLMClient` provides:

### Notebook Operations (NotebookMixin)

- `list_notebooks()` - List all notebooks with metadata
- `get_notebook(notebook_id)` - Get notebook details
- `get_notebook_summary(notebook_id)` - Get AI-generated summary
- `create_notebook(title)` - Create new notebook
- `rename_notebook(notebook_id, title)` - Rename notebook
- `configure_chat(notebook_id, goal, custom_prompt, response_length)` - Configure chat behavior
- `delete_notebook(notebook_id)` - Delete notebook (permanent!)

### Source Operations (SourceMixin)

- `add_url_source(notebook_id, url, title)` - Add URL or YouTube video
- `add_text_source(notebook_id, text, title)` - Add pasted text snippet
- `add_drive_source(notebook_id, drive_id)` - Add Google Drive file
- `upload_file(notebook_id, file_path)` - Upload local file
- `get_notebook_sources_with_types(notebook_id)` - List sources with metadata
- `delete_source(notebook_id, source_id)` - Delete source
- `get_source_fulltext(source_id)` - Get raw text content
- `wait_for_source_ready(notebook_id, source_id, timeout)` - Wait for processing

### Conversation Operations (ConversationMixin)

- `query(notebook_id, question)` - Ask a question
- `get_conversation_history(notebook_id)` - Get chat history
- `clear_conversation(notebook_id)` - Clear chat

### Studio Operations (StudioMixin)

- `create_audio_overview(notebook_id)` - Generate audio overview
- `create_study_guide(notebook_id)` - Generate study guide
- `create_briefing_doc(notebook_id)` - Generate briefing document
- `create_faq(notebook_id)` - Generate FAQ
- `create_timeline(notebook_id)` - Generate timeline
- `poll_studio_status(notebook_id, artifact_type)` - Check generation status
- `delete_studio_artifact(notebook_id, artifact_type)` - Delete artifact

## Example Workflow

```bash
# 1. Create a new notebook
NOTEBOOK_ID=$(python3 scripts/create_notebook.py --title "AI Research" --json | jq -r '.id')

# 2. Add sources
python3 scripts/add_source.py "$NOTEBOOK_ID" --url "https://arxiv.org/abs/2301.00001" --wait
python3 scripts/add_source.py "$NOTEBOOK_ID" --url "https://arxiv.org/abs/2302.00001" --wait

# 3. List sources to verify
python3 scripts/list_sources.py "$NOTEBOOK_ID"

# 4. Ask questions
python3 scripts/query.py "$NOTEBOOK_ID" --question "What are the key differences between these papers?"
```

## Advantages

1. **Zero MCP dependencies** - No MCP server or protocol required
2. **Fully vendored** - Library included as git submodule, no external installs
3. **Direct HTTP access** - Simple, fast, debuggable
4. **Standalone** - Works independently of any MCP infrastructure
5. **Full API access** - Can use any method from notebooklm_tools
6. **Self-contained** - Git submodule keeps everything in the skill directory

## Submodule Information

- **Repository**: https://github.com/jacob-bd/notebooklm-mcp-cli
- **Vendored at**: `vendor/notebooklm-mcp-cli/`
- **Library path**: `vendor/notebooklm-mcp-cli/src/notebooklm_tools/`
- **Update**: `git submodule update --remote`

## Troubleshooting

### Submodule not initialized

```bash
cd ~/.claude/skills/notebooklm
git submodule update --init --recursive
```

### Import errors

Make sure `httpx` is installed:

```bash
pip install httpx
```

### Authentication errors

Re-export cookies from browser:

```bash
source ~/.claude/skills/ai-browser/tools/jarvis.sh
jarvis_cookies_save
jarvis_cookies_export_mcp
```

## Related Skills

- **ai-browser**: Use for initial login and cookie export
- **google-services**: Similar pattern for Gmail, Drive, Docs access (uses OAuth instead of cookies)
