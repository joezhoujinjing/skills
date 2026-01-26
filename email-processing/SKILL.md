---
name: email-processing
description: Email triage and processing system based on GTD principles. Use when the user asks for help with email management, inbox overwhelm, email workflow, responding to emails, or reaching inbox zero. Helps transform email from a source of distraction into a controlled input channel.
---

# Email Processing Skill

Email is other people's priorities arriving in your space. Process it quickly into your system, then get back to meaningful work.

## Core Principles

1. **Process, don't check** — Touch each email once, make a decision, move it out
2. **Batch into blocks** — 2-3 scheduled times daily, email closed otherwise
3. **Inbox is not a task list** — Extract actions to your task system
4. **2-minute rule** — If it takes less, do it now

## The Decision Tree

```
Is it actionable?
├── NO →
│   ├── Delete (no value)
│   ├── Archive (reference)
│   └── Someday/Maybe (future idea)
└── YES → What's the next action?
    ├── < 2 min → Do it NOW
    └── > 2 min →
        ├── Delegate → Forward + Waiting For list
        └── Keep → Extract to task system, archive email
```

## Email Block Routine (15-30 min)

1. Scan for truly urgent items (rare)
2. Process top-to-bottom, one decision per email
3. Target inbox zero
4. Close email until next block

## Suggested Schedule

| Block | Time | Purpose |
|-------|------|---------|
| Morning | 9:00am | Process overnight items |
| Midday | 1:00pm | Catch urgent replies |
| End of day | 4:30pm | Clear before shutdown |

Protect morning focus hours — don't start the day in email.

## Folder Structure (Keep Simple)

- **Inbox** — Temporary, process to zero
- **@Action** — Items needing >2 min work (optional, prefer external task system)
- **@Waiting** — Sent items awaiting reply
- **Archive** — Everything else worth keeping

## Quick Response Templates

**Acknowledge + Timeline**: "Got it—I'll have this by [date]."

**Delegate**: "Looping in [Name] who can help with this."

**Decline**: "Can't take this on right now. Have you tried [alternative]?"

**Defer**: "On my radar. I'll follow up by [date]."

## Rules

- Never use inbox as a reminder system
- Never leave emails "unread" as markers
- Never process email during deep work
- Set expectations: you don't reply instantly

## Extracting Actions to Trello

When an email requires real work (>2 min), create a Trello card with the email context:

### Process

1. Identify the concrete next action from the email
2. Create a Trello card with email metadata
3. Archive the email in Gmail
4. The email leaves your inbox; the action lives in Trello

### Card Format

**Card Name**: Clear, actionable task title (start with verb)

**Card Description**:
```
## Email Context
- **From**: {sender name} <{sender email}>
- **Date**: {received date}
- **Subject**: {original subject}

## Original Message
{relevant excerpt or full body}

## Next Action
{what specifically needs to be done}

## Due Date
{if mentioned or implied in email}
```

### Example

Email: "Hi, can you review the Q4 budget proposal and send feedback by Friday?"

**Card Name**: Review Q4 budget proposal and send feedback

**Card Description**:
```
## Email Context
- **From**: Sarah Chen <sarah@company.com>
- **Date**: 2024-01-15
- **Subject**: Q4 Budget Review Request

## Original Message
Hi, can you review the Q4 budget proposal and send feedback by Friday?
The document is in the shared drive under Finance/Q4.

## Next Action
1. Open Q4 budget proposal in shared drive
2. Review line items and assumptions
3. Reply to Sarah with feedback

## Due Date
Friday (2024-01-19)
```

### Creating the Card

```bash
# Get credentials
TRELLO_API_KEY=$(gcloud secrets versions access latest --secret="trello-api-key")
TRELLO_TOKEN=$(gcloud secrets versions access latest --secret="trello-token")

# Create card with email context
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={actionListId}" \
  -d "name=Review Q4 budget proposal and send feedback" \
  -d "desc=## Email Context
- **From**: Sarah Chen <sarah@company.com>
- **Date**: 2024-01-15
- **Subject**: Q4 Budget Review Request

## Original Message
Hi, can you review the Q4 budget proposal and send feedback by Friday?

## Next Action
Review and reply with feedback

## Due Date
2024-01-19" \
  -d "due=2024-01-19T17:00:00.000Z"
```

### Tips

- Use a dedicated "📥 Inbox" or "@Action" list in Trello for email-derived tasks
- Add labels for email source (e.g., "from-email") to track origin
- Link back to the email if needed using Gmail message ID in the description
