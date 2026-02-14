# Email Processing Skill

GTD-based email processing system with both interactive and automated workflows.

## Quick Start

### For Remote/Automated Processing (Recommended)

```bash
cd ~/.claude/skills/email-processing

# Full automated workflow
python scripts/export_unprocessed.py          # 1. Fetch emails
python scripts/process_emails_automated.py     # 2. Auto-process with rules
# 3. Review data/emails_to_review.yaml (with Claude's help)
python scripts/export_unprocessed.py --verify  # 4. Verify inbox zero
```

**What it does:**

- Auto-archives: newsletters, notifications, receipts, calendar invites
- Saves for review: urgent emails, internal emails, direct messages
- Creates: `data/emails_to_review.yaml` with suggested actions

### For Interactive Processing (Manual)

```bash
cd ~/.claude/skills/email-processing

python scripts/export_unprocessed.py           # 1. Fetch emails
python scripts/process_emails_gtd.py            # 2. See analysis
python scripts/process_emails_interactive.py    # 3. Process one-by-one
python scripts/export_unprocessed.py --verify   # 4. Verify inbox zero
```

## Files Overview

### Main Scripts

- `export_unprocessed.py` - Fetch emails from Gmail to YAML
- `process_emails_automated.py` - **Auto-process with rules (remote mode)**
- `process_emails_interactive.py` - Interactive one-by-one processing
- `process_review_list.py` - Process the review list interactively
- `process_emails_gtd.py` - Analysis and recommendations

### Supporting Scripts

- `send_reply.py` - Quick reply to emails
- `create_trello_card.py` - Create Trello cards from emails
- `batch_archive_by_category.py` - Batch archive by category
- `show_urgent_emails.py` - Show only urgent emails

### Configuration

- `processing_rules.yaml.example` - Customizable processing rules
- `.gitignore` - Excludes email dumps from git

### Documentation

- `SKILL.md` - Full skill documentation with both workflows
- `REMOTE_WORKFLOW.md` - Guide for remote processing with Claude
- `README.md` - This file

## Using with Claude Code

Just ask Claude:

> "Process my emails"

Claude will:

1. Run the automated workflow
2. Show you what was processed
3. Present emails needing your review
4. Help you draft replies or create Trello cards
5. Verify inbox zero

See `REMOTE_WORKFLOW.md` for detailed examples.

## Customization

Copy the example rules and customize:

```bash
cp processing_rules.yaml.example processing_rules.yaml
# Edit with your domains, keywords, etc.
```

## Output Files (gitignored)

- `data/emails_dump.yaml` - Raw email data from Gmail
- `data/emails_to_review.yaml` - Emails needing manual review
- `emails_for_trello.yaml` - Suggested Trello cards
- `~/email_triage/unread_emails_*.yaml` - Timestamped backups

## Integration

Works with:

- Gmail API (via google-services skill)
- Trello API (via trello skill)
- Claude Code for remote control

## Daily Routine (5 minutes)

```bash
# Morning - automated triage
python scripts/export_unprocessed.py && python scripts/process_emails_automated.py

# Ask Claude: "Show me my priority emails"
# Claude helps you decide on each one

# Verify
python scripts/export_unprocessed.py --verify
```

That's it! Inbox zero in 5 minutes.
