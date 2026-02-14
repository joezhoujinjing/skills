# Email Processing

GTD-based email triage with LLM intelligence, rule engine, and Trello integration.

## Usage

```bash
# Run from the skill root (directory containing SKILL.md)

# Process emails
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor joe@multifi.ai

# Limit to N emails
PYTHONPATH=src:$PYTHONPATH python3 -m email_processor joe@multifi.ai 10
```

## How It Works

1. **Fetch** emails from Gmail inbox (batch API)
2. **Rules engine** handles routine emails (~80%): newsletters, receipts, notifications
3. **LLM triage** (Gemini 3 Flash) categorizes ambiguous emails (~20%)
4. **Auto-actions**: archive low-value, create Trello cards for tasks
5. **Interactive review**: index-based UI for remaining emails
6. **File storage**: all emails and decisions saved to `data/`

## Project Structure

```
email-processing/
  config/
    config.json          # All settings (accounts, LLM, Trello, storage)
    rules.yaml           # Rule engine patterns
  src/email_processor/
    __main__.py           # CLI entry point
    models/email.py       # Email, TriageDecision, ReviewItem
    core/
      gmail.py            # Gmail API (batch fetch, archive)
      rules_engine.py     # Structured rule matching
      llm_triage.py       # LangChain + Gemini structured output
      trello.py           # Multi-board routing (LLM-driven)
      secrets.py          # gsm: prefix for Google Secret Manager
    storage/
      file_storage.py     # Date-organized file storage
    cli/
      process.py          # Main orchestrator
      review.py           # Interactive review interface
  data/                   # Runtime data (gitignored)
    <account>/
      emails/<YYYY-MM-DD>/<message_id>/
      sessions/<session_id>/
      index/
```

## Configuration

All in `config/config.json`. Secrets use `gsm:` prefix to fetch from Google Secret Manager, or raw values directly.

```json
{
  "llm": {
    "api_key": "gsm:nexus-hub-google-api-key"
  },
  "accounts": {
    "joe@multifi.ai": {
      "gmail_refresh_token": "gsm:google-all-services-refresh-token-joe-multifi-ai",
      "default_trello_board": "multifi"
    }
  },
  "trello": {
    "credentials": {
      "api_key": "gsm:trello-api-key",
      "token": "gsm:trello-token"
    }
  }
}
```

## Trello Boards

6 boards, always selected by LLM:
**multifi** | **personal** | **nexus** | **clinview** | **huiya** | **inbox** (catch-all)

## Review Commands

```
<numbers>         Review emails (e.g., "1 2 5" or "1-4")
archive <range>   Bulk archive (e.g., "archive 10-20")
trello <range>    Create Trello cards (e.g., "trello 1-5")
show <category>   Filter (urgent/important/other)
list              Show list again
done              Finish session
```

## Dependencies

- `google-api-python-client`, `google-auth` - Gmail API
- `langchain-google-genai` - LLM triage (Gemini)
- `pyyaml` - Rules config
- `gcloud` CLI - Secret Manager access
