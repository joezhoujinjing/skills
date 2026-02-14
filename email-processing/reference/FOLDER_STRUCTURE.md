# Email Processing Skill - Folder Structure

```
email-processing/
├── README.md                    # Quick start guide
├── SKILL.md                     # Complete skill documentation
├── .gitignore                   # Excludes personal data
│
├── scripts/                     # All executable Python scripts
│   ├── export_unprocessed.py           # Main: Fetch emails from Gmail
│   ├── export_all_inbox.py             # Utility: Fetch all inbox emails
│   ├── export_all_unread.py            # Utility: Fetch all unread emails
│   ├── process_emails_automated.py     # Main: Auto-process with rules
│   ├── process_emails_interactive.py   # Main: Interactive processing
│   ├── process_emails_gtd.py           # Analysis: GTD categorization
│   ├── process_review_list.py          # Process review items
│   ├── mark_all_read.py                # Utility: Bulk mark as read
│   ├── archive_all_inbox.py            # Utility: Archive all inbox
│   ├── send_reply.py                   # Action: Send email reply
│   ├── create_trello_card.py           # Action: Create Trello card
│   ├── check_gmail_status.py           # Debug: Check account status
│   ├── check_inbox_count.py            # Debug: Quick inbox counter
│   ├── verify_tokens.py                # Debug: Verify OAuth tokens
│   └── [other utility scripts]
│
├── data/                        # Email data and config (gitignored)
│   ├── emails_dump.yaml                # Fetched emails (gitignored)
│   ├── emails_to_review.yaml           # Items needing review (gitignored)
│   ├── processing_rules.yaml.example   # Example processing rules
│   └── [other YAML dumps]              # All personal data here
│
└── reference/                   # Documentation and guides
    ├── REMOTE_WORKFLOW.md              # Claude Code integration guide
    └── FOLDER_STRUCTURE.md             # This file

```

## Why This Structure?

### scripts/

- All executable Python scripts in one place
- Easy to find and run scripts
- Clear separation from documentation

### data/

- All email dumps and personal data isolated
- Everything in this folder is gitignored (except examples)
- Safe from accidental commits
- Easy to clean up (`rm -rf data/*.yaml`)

### reference/

- Supporting documentation that isn't primary
- Workflow guides and examples
- Architecture documentation

## Running Scripts

Always run scripts from the skill directory root:

```bash
cd ~/.claude/skills/email-processing

# Main workflow
python scripts/export_unprocessed.py
python scripts/process_emails_automated.py

# Utilities
python scripts/check_gmail_status.py
python scripts/mark_all_read.py

# Actions
python scripts/send_reply.py --message-id {id}
python scripts/create_trello_card.py --message-id {id}
```

## Data Files

All data files are stored in `data/` and gitignored:

- `data/emails_dump.yaml` - All fetched emails
- `data/emails_to_review.yaml` - Items needing manual review
- `data/emails_for_trello.yaml` - Suggested Trello cards
- `data/processing_rules.yaml` - Custom rules (copy from .example)

## Benefits

1. **Clear organization** - Know where everything is
2. **Safe commits** - Personal data isolated in data/
3. **Easy maintenance** - Scripts grouped by function
4. **Better documentation** - Reference materials separate
5. **Clean root** - Only essential files in root directory
