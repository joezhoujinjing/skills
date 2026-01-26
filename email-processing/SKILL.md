---
name: email-processing
description: Email triage and processing system based on GTD principles. Use when the user asks for help with email management, inbox overwhelm, email workflow, responding to emails, or reaching inbox zero. Helps transform email from a source of distraction into a controlled input channel.
---

# Email Processing Skill

Email is other people's priorities arriving in your space. Process it quickly into your system, then get back to meaningful work.

## Core Principles

1. **Process, don't check** — Touch each email once, make a decision, move it out
2. **Batch into blocks** — 2-3 scheduled times daily (9am, 1pm, 4:30pm), email closed otherwise
3. **Inbox is not a task list** — Extract actions to Trello
4. **2-minute rule** — If it takes less, do it now

## Decision Tree

```
Is it actionable?
├── NO → Delete / Archive / Someday
└── YES → What's the next action?
    ├── < 2 min → Do it NOW (reply/forward)
    └── > 2 min → Create Trello card, archive email
```

## Folder Structure

- **Inbox** — Temporary, process to zero
- **@Waiting** — Sent items awaiting reply
- **Archive** — Everything else

## Reply & Forward Commands

```bash
# Reply to sender
python scripts/gmail_api.py reply --message-id {id} --body "Message"

# Reply all
python scripts/gmail_api.py reply --message-id {id} --reply-all --body "Message"

# Reply to specific people
python scripts/gmail_api.py reply --message-id {id} --to "a@ex.com, b@ex.com" --body "Message"

# Forward (new thread)
python scripts/gmail_api.py forward --message-id {id} --to "delegate@ex.com" --body "Optional note"
```

## Create Trello Card from Email

When email requires >2 min work, create a Trello card:

```bash
# Create card with default settings (multifi board, To Do list, due tomorrow)
python create_trello_card.py --message-id {message_id} \
  --action "What needs to be done"

# Create card with custom title and due date
python create_trello_card.py --message-id {message_id} \
  --title "Custom Task Title" \
  --action "Detailed action items" \
  --due-days 3

# Create card in different board/list
python create_trello_card.py --message-id {message_id} \
  --board "personal" \
  --list "Doing" \
  --action "Action description"
```

**Card format** (auto-generated):
```
## Email Context
- From: {sender}
- Date: {date}
- Subject: {subject}

## Original Message
{email snippet}

## Next Action
{your action notes}
```

## Rules

- Never use inbox as a reminder system
- Never leave emails "unread" as markers
- Never process email during deep work
