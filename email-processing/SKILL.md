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
- **File-based storage**: Date-organized emails under `data/`
- **Secret management**: `gsm:` prefix for Google Secret Manager, or raw values

## How It Works

```
Inbox -> Rules Engine -> LLM Triage -> Auto-Actions -> Review -> File Storage
          (archive)      (categorize)   (archive/trello)  (interactive)
```

## Configuration

Single config file: `config/config.json` (accounts, LLM, Trello, storage).
Rules: `config/rules.yaml`.

## Daily Workflow

1. Run the command for your email account
2. System auto-archives and creates Trello cards
3. Review flagged emails with index-based UI
4. Achieve inbox zero
