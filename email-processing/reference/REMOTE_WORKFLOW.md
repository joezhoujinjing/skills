# Remote Email Processing Workflow

Use this when controlling your email processing remotely via Claude Code.

## Quick Start (Automated Mode)

```bash
# Navigate to skill directory
cd ~/.claude/skills/email-processing

# 1. Fetch emails from Gmail
python scripts/export_unprocessed.py

# 2. Auto-process with rules
python scripts/process_emails_automated.py

# 3. Review the summary and check data/emails_to_review.yaml
```

## Working with Claude Code

After running automated processing, you can work with Claude to handle the review list:

### Example Session

**You:** "Process my emails using the email-processing skill"

**Claude:** _Runs export_unprocessed.py and process_emails_automated.py_

**Claude:** "I've processed 45 emails:

- 32 auto-archived (newsletters, notifications)
- 13 need your review (saved to data/emails_to_review.yaml)

Let me show you the priority items..."

**You:** "Show me the urgent ones first"

**Claude:** _Reads data/emails_to_review.yaml and shows urgent emails_

"Here are 3 urgent emails:

1. **Action Required: Q4 Budget Approval**
   - From: finance@multifi.ai
   - Needs approval by Friday

   Suggested actions:
   - Quick reply if you approve
   - Create Trello card to review details"

**You:** "Create a Trello card for #1, archive the rest"

**Claude:** _Executes create_trello_card.py for email #1, archives others_

## Commands for Claude

When working with Claude remotely, you can ask:

- "Process my emails" (runs full automated workflow)
- "Show me emails needing review"
- "Create Trello cards for all urgent emails"
- "Archive all newsletters"
- "Reply to [email] with [message]"
- "What's left in my inbox?"

## Output Files

After automated processing, check these files:

- `data/emails_to_review.yaml` - Emails needing your attention
- `data/emails_for_trello.yaml` - Suggested for Trello cards (if any)
- `data/emails_dump.yaml` - Full email dump (gitignored)

## Customizing Rules

Copy and customize the rules:

```bash
cp processing_rules.yaml.example processing_rules.yaml
# Edit processing_rules.yaml with your preferences
```

Rules you can customize:

- Auto-archive domains (add your newsletter sources)
- Always-review domains (add your company domain)
- Urgent keywords
- Auto-Trello keywords

## Daily Routine (5 minutes)

```bash
# Morning email check
cd ~/.claude/skills/email-processing
python scripts/export_unprocessed.py && python scripts/process_emails_automated.py

# Review summary output
# Ask Claude to help with data/emails_to_review.yaml

# Verify inbox zero
python scripts/export_unprocessed.py --verify
```

## Integration with Claude Code

The skill is designed to work seamlessly with Claude Code:

1. **Automated triage** - Claude runs the automated script
2. **Smart suggestions** - Claude reads the review list and suggests actions
3. **One-command execution** - Claude can reply/archive/create Trello cards
4. **Contextual help** - Claude sees full email context and can draft replies

This gives you the best of both worlds:

- Automation handles the noise (newsletters, notifications)
- Claude helps with decisions on important emails
- You review and approve Claude's suggestions remotely
