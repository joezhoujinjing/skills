---
name: email-processing
description: Email triage and processing system based on GTD principles. Use when the user asks for help with email management, inbox overwhelm, email workflow, responding to emails, or reaching inbox zero. Helps transform email from a source of distraction into a controlled input channel.
---

# Email Processing Skill

GTD-based email triage with LLM intelligence and Trello integration.

## Quick Start

```bash
# Run from the skill root (directory containing this SKILL.md)
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor joe@multifi.ai
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor joezhoujinjing@gmail.com
```

## Features

- **Hybrid processing**: Rules (~80%) + Gemini 3 Flash LLM (~20%)
- **Smart Trello routing**: LLM selects from 6 boards (multifi, personal, nexus, clinview, huiya, inbox)
- **Index-based review**: One-step commands for emails needing attention
- **Full-text search**: Search across sender, subject, body, attachments, and decisions
- **File-based storage**: Date-organized emails with full body and attachment references under `data/`
- **Secret management**: `gsm:` prefix for Google Secret Manager, or raw values

## How It Works

```
Inbox -> Rules Engine -> LLM Triage -> Auto-Actions -> Review -> File Storage
          (archive)      (categorize)   (archive/trello)  (interactive)
```

## Configuration

Single config file: `config/config.json` (accounts, LLM, Trello, storage).
Rules: `config/rules.yaml`.

## Search

```bash
# Search all accounts
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor search "invoice"

# Filter by account, date, category, or action
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor search "vanta" --account joe@multifi.ai
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor search "budget" --from 2026-02-01 --to 2026-02-14
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor search --category urgent --action trello
```

Searches across: sender, recipient, subject, snippet, body, category, and decision reason.

## Email Data & Attachments

Emails stored at `data/<account>/emails/<YYYY-MM-DD>/<message_id>/email.json` with full body, attachment refs, and decisions.

Each attachment has `filename`, `mimeType`, `size`, and `attachmentId`. To download:
```python
data = service.users().messages().attachments().get(
    userId='me', messageId=message_id, id=attachment_id).execute()
file_bytes = base64.urlsafe_b64decode(data['data'])
```

## Daily Workflow

1. Run the command for your email account
2. System auto-archives and creates Trello cards
3. Review flagged emails with index-based UI
4. Achieve inbox zero
