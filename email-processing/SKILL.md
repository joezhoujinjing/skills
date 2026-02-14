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
python scripts/create_trello_card.py --message-id {message_id} \
  --action "What needs to be done"

# Create card with custom title and due date
python scripts/create_trello_card.py --message-id {message_id} \
  --title "Custom Task Title" \
  --action "Detailed action items" \
  --due-days 3

# Create card in different board/list
python scripts/create_trello_card.py --message-id {message_id} \
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

## Standard Operating Procedure (SOP)

### Choose Your Workflow

**Interactive Mode** (local/manual processing)

- Best for: First time, weekly reviews, when you want full control
- Time required: 30-60 minutes

**Automated Mode** (remote/headless processing)

- Best for: Daily processing, remote control via Claude Code
- Time required: 5-10 minutes review time

---

### Workflow A: Interactive (Local Processing)

Follow this 4-step process to achieve inbox zero:

**Step 1: Collect All Inbox Emails**

```bash
python scripts/export_unprocessed.py
```

- Fetches all unread/inbox emails via Gmail API
- Saves to `emails_dump.yaml` in skill directory (gitignored)
- Creates backup with timestamp

**Step 2: Analyze & Categorize**

```bash
python scripts/process_emails_gtd.py
```

- Analyzes email patterns (domain, category, urgency)
- Shows quick wins (newsletters, notifications, receipts)
- Highlights action-required and direct messages

**Step 3: Interactive Processing**

```bash
python scripts/process_emails_interactive.py
```

For each email, choose:

- **a) No reply needed** — Archive immediately
- **b) Quick reply (<2 min)** — Reply via gmail_api.py, then archive
- **c) Create Trello card (>2 min)** — Extract action, archive email

The script walks through priority order:

1. Urgent/action-required first
2. Direct messages second
3. Remaining emails by category

**Step 4: Verify Inbox Zero**

```bash
python scripts/export_unprocessed.py --verify
```

- Confirms inbox is empty
- Shows remaining count if any
- Celebrates success 🎉

---

### Workflow B: Automated (Remote Processing)

Perfect for remote control via Claude Code or daily automation:

**Step 1: Collect All Inbox Emails**

```bash
python scripts/export_unprocessed.py
```

Same as interactive mode - fetches all emails to `emails_dump.yaml`

**Step 2: Automated Processing with Rules**

```bash
python scripts/process_emails_automated.py
```

- Automatically processes emails based on predefined rules:
  - **Auto-archive:** Newsletters, notifications, receipts, calendar invites
  - **Save for review:** Urgent, internal, direct messages
  - **Suggest Trello:** Complex items needing action
- Creates `emails_to_review.yaml` with items needing attention
- Shows processing summary

**Step 3: Review Priority Items**

```bash
python process_review_list.py
```

Or work with Claude Code to process `emails_to_review.yaml`:

- For each email, Claude can help you decide:
  - Archive with no action
  - Draft and send quick replies
  - Create Trello cards with suggested actions

**Step 4: Verify Inbox Zero**

```bash
python scripts/export_unprocessed.py --verify
```

Same verification step - confirms inbox is empty

### Processing Rules (Customizable)

Default auto-archive rules in `process_emails_automated.py`:

- **Newsletters:** substack.com, medium.com, beehiiv.com
- **Notifications:** LinkedIn, GitHub, SaaS tools
- **Receipts:** Stripe, Mercury, Bill.com
- **Calendar:** All calendar invites (assuming already handled)

Always requires review:

- Urgent/action-required keywords
- Internal emails (@multifi.ai)
- Direct messages from people
- Anything not matching auto-archive rules

### Quick Commands Reference

```bash
# Quick reply (2-minute rule)
python scripts/send_reply.py --message-id {id} --body "Thanks! Done."

# Create Trello card for longer work
python scripts/create_trello_card.py --message-id {id} \
  --action "Review Q4 budget proposal by Friday"

# Batch archive by category
python scripts/batch_archive_by_category.py --category newsletter
```

## Rules

- Never use inbox as a reminder system
- Never leave emails "unread" as markers
- Never process email during deep work
- Always complete all 4 SOP steps in one session
