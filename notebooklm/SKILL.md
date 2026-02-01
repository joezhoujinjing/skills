---
name: notebooklm
description: "Browser automation for Google NotebookLM using ai-dev-browser. Use to list notebooks, ask questions, add/list/remove sources, create/open/delete notebooks, and download source content."
---

# NotebookLM (ai-dev-browser)

Automate Google NotebookLM using the Jarvis browser profile and ai-dev-browser tools.

## Setup (one-time)

1. Install ai-dev-browser (library) if not already available in your Python env.
2. Log in using the Jarvis profile:

```bash
python tools/auth_manager.py setup
```

## Core commands

```bash
python tools/list_notebooks.py
python tools/open_notebook.py --name "My Notebook"
python tools/create_notebook.py --name "My Notebook"
python tools/delete_notebook.py --name "My Notebook" --confirm
python tools/ask_question.py --notebook-name "My Notebook" --question "..."
python tools/list_sources.py --notebook-name "My Notebook"
python tools/add_source.py --notebook-name "My Notebook" --url "https://..."
python tools/add_source.py --notebook-name "My Notebook" --file "/path/to/file.pdf"
python tools/remove_source.py --notebook-name "My Notebook" --source "Source Name"
python tools/download_source.py --notebook-name "My Notebook" --source "Source Name" --out /tmp/source.txt
```

## Notes

- Uses Jarvis profile for persistent Google login.
- If selectors change, update `tools/selectors.py`.
- File uploads rely on a visible browser window.
