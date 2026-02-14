---
name: google-services
description: Comprehensive Google API access via OAuth 2.0. Use when Claude needs to work with Gmail, Drive, Docs, Sheets, Calendar, Slides, or Forms for listing/searching/reading/creating/updating content, sending email, or managing files/events.
---

Base directory for this skill: /Users/jinjingzhou/.claude/skills/google-services

# Google Services Skill

Comprehensive Google API access for AI agents using OAuth 2.0 authentication.

## Prerequisites

- Python packages: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`
- OAuth credentials in secret-vault:
  - `NEXUS_OAUTH_GOOGLE_CLIENT_ID`
  - `NEXUS_OAUTH_GOOGLE_CLIENT_SECRET`
- Refresh token in secret-vault (e.g., `google-all-services-refresh-token-EMAIL`)

## Installation

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Available Services

### Gmail

- List messages (inbox, sent, drafts)
- Search emails by query
- Read email content
- Send emails
- Create drafts
- Manage labels
- Mark as read/unread

### Google Drive

- List files and folders
- Search files
- Download files
- Upload files
- Create folders
- Share files/folders
- Move/rename files
- Delete files

### Google Docs

- Create documents
- Read document content
- Update document content
- Format text
- Insert images/tables

### Google Sheets

- Create spreadsheets
- Read cell data
- Update cells
- Format cells
- Create charts
- Manage worksheets

### Google Calendar

- List calendars
- List events
- Create events
- Update events
- Delete events
- Search events

### Google Slides

- Create presentations
- Read slides
- Update slides
- Add images/shapes
- Format elements

### Google Forms

- List forms
- Get form structure
- Read responses

## Commands

### `/google-services gmail list [--max-results N] [--query QUERY]`

List Gmail messages.

```bash
python scripts/gmail_api.py list --max-results 20
python scripts/gmail_api.py list --query "from:someone@example.com"
python scripts/gmail_api.py list --query "is:unread"
```

### `/google-services gmail read <message-id>`

Read a specific email.

```bash
python scripts/gmail_api.py read <message-id>
```

### `/google-services gmail send --to EMAIL --subject SUBJECT --body BODY`

Send an email.

```bash
python scripts/gmail_api.py send \
  --to "recipient@example.com" \
  --subject "Hello" \
  --body "This is a test email"
```

### `/google-services gmail search <query>`

Search emails.

```bash
python scripts/gmail_api.py search "subject:important"
python scripts/gmail_api.py search "has:attachment after:2026/01/01"
```

### `/google-services drive list [--folder-id ID] [--max-results N]`

List files in Google Drive.

```bash
python scripts/drive_api.py list
python scripts/drive_api.py list --folder-id "abc123" --max-results 50
```

### `/google-services drive search <query>`

Search files in Drive.

```bash
python scripts/drive_api.py search "name contains 'report'"
python scripts/drive_api.py search "mimeType='application/pdf'"
```

### `/google-services drive download <file-id> --output PATH`

Download a file from Drive.

```bash
python scripts/drive_api.py download abc123 --output ~/Downloads/file.pdf
```

### `/google-services drive upload <file-path> [--folder-id ID] [--name NAME]`

Upload a file to Drive.

```bash
python scripts/drive_api.py upload ~/Documents/file.pdf
python scripts/drive_api.py upload file.txt --folder-id "abc123" --name "New Name.txt"
```

### `/google-services calendar list-events [--calendar-id ID] [--max-results N]`

List calendar events.

```bash
python scripts/calendar_api.py list-events
python scripts/calendar_api.py list-events --max-results 50
```

### `/google-services calendar create-event --summary TITLE --start DATETIME --end DATETIME`

Create a calendar event.

```bash
python scripts/calendar_api.py create-event \
  --summary "Team Meeting" \
  --start "2026-02-01T10:00:00" \
  --end "2026-02-01T11:00:00" \
  --description "Weekly sync"
```

### `/google-services docs create --title TITLE [--content TEXT]`

Create a Google Doc.

```bash
python scripts/docs_api.py create --title "My Document"
python scripts/docs_api.py create --title "Report" --content "Initial content"
```

### `/google-services docs read <document-id>`

Read a Google Doc.

```bash
python scripts/docs_api.py read abc123
```

### `/google-services sheets create --title TITLE [--sheet-name NAME]`

Create a Google Sheet.

```bash
python scripts/sheets_api.py create --title "Budget 2026"
python scripts/sheets_api.py create --title "Data" --sheet-name "Q1 Results"
```

### `/google-services sheets read <spreadsheet-id> --range RANGE`

Read data from a sheet.

```bash
python scripts/sheets_api.py read abc123 --range "Sheet1!A1:D10"
```

### `/google-services sheets update <spreadsheet-id> --range RANGE --values VALUES`

Update cells in a sheet.

```bash
python scripts/sheets_api.py update abc123 \
  --range "Sheet1!A1:B2" \
  --values "[[\"Name\",\"Value\"],[\"Item1\",\"100\"]]"
```

## Configuration

All scripts automatically use OAuth credentials from secret-vault:

- `NEXUS_OAUTH_GOOGLE_CLIENT_ID`
- `NEXUS_OAUTH_GOOGLE_CLIENT_SECRET`
- Refresh token (specify via `--refresh-token-secret` or set default in script)

Default refresh token secret name: `google-all-services-refresh-token-joezhoujinjing-gmail-com`

## Common Use Cases

### Check unread emails

```bash
/google-services gmail search "is:unread"
```

### Find recent PDFs in Drive

```bash
/google-services drive search "mimeType='application/pdf' modifiedTime > '2026-01-01'"
```

### List today's calendar events

```bash
/google-services calendar list-events --max-results 20
```

### Create a meeting note

```bash
/google-services docs create --title "Meeting Notes - $(date +%Y-%m-%d)"
```

## API Documentation

- [Gmail API](https://developers.google.com/gmail/api)
- [Drive API](https://developers.google.com/drive/api)
- [Calendar API](https://developers.google.com/calendar/api)
- [Docs API](https://developers.google.com/docs/api)
- [Sheets API](https://developers.google.com/sheets/api)
- [Slides API](https://developers.google.com/slides/api)

## Notes

- All API calls require valid OAuth scope access
- Rate limits apply per Google Workspace quotas
- Tokens are refreshed automatically
- Files are created in the authenticated user's account
