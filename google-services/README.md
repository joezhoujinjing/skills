# Google Services Skill

Comprehensive Google API access for AI agents using OAuth 2.0 authentication.

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/jinjingzhou/.claude/skills/google-services
pip install -r requirements.txt
```

### 2. Verify OAuth Credentials

Ensure you have the following secrets in secret-vault:

- `NEXUS_OAUTH_GOOGLE_CLIENT_ID`
- `NEXUS_OAUTH_GOOGLE_CLIENT_SECRET`
- `google-all-services-refresh-token-joezhoujinjing-gmail-com` (or your refresh token)

### 3. Test the Skill

```bash
# List recent emails
python scripts/gmail_api.py list --max-results 5

# List Google Drive files
python scripts/drive_api.py list --max-results 10

# List calendar events
python scripts/calendar_api.py list-events
```

## Available Services

This skill provides access to:

- **Gmail**: Read, search, send emails
- **Google Drive**: List, search, upload, download files
- **Google Calendar**: Manage events
- **Google Docs**: Create and read documents
- **Google Sheets**: Create and manage spreadsheets

## Example Usage

### Gmail Examples

```bash
# List unread emails
python scripts/gmail_api.py search --query "is:unread" --max-results 20

# Read a specific email
python scripts/gmail_api.py read --message-id "abc123xyz"

# Send an email
python scripts/gmail_api.py send \
  --to "friend@example.com" \
  --subject "Hello from Claude" \
  --body "This is a test email sent via the Google Services skill!"

# List Gmail labels
python scripts/gmail_api.py labels
```

### Google Drive Examples

```bash
# List all files
python scripts/drive_api.py list --max-results 20

# Search for PDFs
python scripts/drive_api.py search --query "mimeType='application/pdf'"

# Upload a file
python scripts/drive_api.py upload --file-path ~/Documents/report.pdf

# Download a file
python scripts/drive_api.py download --file-id "abc123" --output ~/Downloads/file.pdf

# Create a folder
python scripts/drive_api.py create-folder --name "My New Folder"
```

### Google Calendar Examples

```bash
# List upcoming events
python scripts/calendar_api.py list-events --max-results 10

# Create an event
python scripts/calendar_api.py create-event \
  --summary "Team Meeting" \
  --start "2026-02-01T10:00:00" \
  --end "2026-02-01T11:00:00" \
  --description "Weekly team sync"

# List all calendars
python scripts/calendar_api.py list-calendars
```

### Google Docs Examples

```bash
# Create a new document
python scripts/docs_api.py create --title "Meeting Notes" --content "Initial content here"

# Read a document
python scripts/docs_api.py read --document-id "abc123"

# Append text to a document
python scripts/docs_api.py append --document-id "abc123" --text "Additional notes..."
```

### Google Sheets Examples

```bash
# Create a new spreadsheet
python scripts/sheets_api.py create --title "Budget 2026" --sheet-name "Q1"

# Read data from a sheet
python scripts/sheets_api.py read \
  --spreadsheet-id "abc123" \
  --range "Sheet1!A1:D10"

# Update cells
python scripts/sheets_api.py update \
  --spreadsheet-id "abc123" \
  --range "Sheet1!A1:B2" \
  --values '[["Name","Value"],["Item1","100"]]'

# Get spreadsheet info
python scripts/sheets_api.py info --spreadsheet-id "abc123"
```

## Architecture

```
google-services/
├── SKILL.md                   # Skill documentation
├── README.md                  # This file
├── requirements.txt           # Python dependencies
└── scripts/
    ├── oauth_helper.py        # Shared OAuth authentication
    ├── gmail_api.py           # Gmail operations
    ├── drive_api.py           # Google Drive operations
    ├── calendar_api.py        # Calendar operations
    ├── docs_api.py            # Docs operations
    └── sheets_api.py          # Sheets operations
```

## Custom Refresh Token

If you want to use a different refresh token, pass the `--refresh-token-secret` parameter:

```bash
python scripts/gmail_api.py list --refresh-token-secret "your-custom-token-secret-name"
```

## API Rate Limits

- Gmail API: 250 quota units/user/second
- Drive API: 12,000 requests/minute
- Calendar API: 1,000,000 requests/day
- Docs API: 300 requests/minute
- Sheets API: 500 requests/100 seconds per project

## Troubleshooting

### "Invalid grant" error

Your refresh token may have expired. Generate a new one using the google-oauth skill.

### "Insufficient permissions" error

Ensure your OAuth token was created with all required scopes. Use the google-oauth skill to generate a token with full access.

### "Module not found" error

Install dependencies: `pip install -r requirements.txt`

## References

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [Google Docs API Documentation](https://developers.google.com/docs/api)
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
