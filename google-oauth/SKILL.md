---
name: google-oauth
description: Generate OAuth 2.0 refresh tokens for Google services (Gmail, Drive, Calendar, etc.). Use this when you need to obtain refresh tokens for accessing Google APIs on behalf of users.
---

# Google OAuth 2.0 Skill

Generate OAuth 2.0 refresh tokens for Google services.

## Prerequisites

- Python package: `google-auth-oauthlib`
- Credentials in secret-vault: `NEXUS_OAUTH_GOOGLE_CLIENT_ID`, `NEXUS_OAUTH_GOOGLE_CLIENT_SECRET`
- Redirect URI configured: Add `http://localhost:XXXX/` (with trailing slash) to [OAuth client](https://console.cloud.google.com/apis/credentials)

## Google API Scopes (Full Access)

| Service         | Scope                                                      |
| --------------- | ---------------------------------------------------------- |
| Gmail           | `https://mail.google.com/`                                 |
| Drive           | `https://www.googleapis.com/auth/drive`                    |
| Docs            | `https://www.googleapis.com/auth/documents`                |
| Sheets          | `https://www.googleapis.com/auth/spreadsheets`             |
| Slides          | `https://www.googleapis.com/auth/presentations`            |
| Calendar        | `https://www.googleapis.com/auth/calendar`                 |
| Forms           | `https://www.googleapis.com/auth/forms.body`               |
| Forms Responses | `https://www.googleapis.com/auth/forms.responses.readonly` |
| Chat Messages   | `https://www.googleapis.com/auth/chat.messages`            |
| Chat Spaces     | `https://www.googleapis.com/auth/chat.spaces`              |
| YouTube         | `https://www.googleapis.com/auth/youtube`                  |
| Contacts        | `https://www.googleapis.com/auth/contacts`                 |
| Photos          | `https://www.googleapis.com/auth/photoslibrary`            |

## Usage

### `/google-oauth get-token <scopes> [--port PORT]`

```bash
python scripts/get_refresh_token.py "<scope1> <scope2> ..." [--port PORT]
```

**Examples:**

```bash
# All services
/google-oauth get-token "https://mail.google.com/ https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/presentations https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/forms.body https://www.googleapis.com/auth/forms.responses.readonly https://www.googleapis.com/auth/chat.messages https://www.googleapis.com/auth/chat.spaces" --port 8085

# Gmail only
/google-oauth get-token "https://mail.google.com/" --port 8085

# Gmail + Drive + Calendar
/google-oauth get-token "https://mail.google.com/ https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar" --port 8085
```

**Store the token:**

```bash
/secret-vault set google-all-services-refresh-token-EMAIL "YOUR_TOKEN"
```

## Troubleshooting

**"Redirect URI mismatch"**: Add `http://localhost:PORT/` (with trailing `/`) to authorized redirect URIs in [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

**"Access blocked"**: Add yourself as test user or publish OAuth consent screen to production

**Browser doesn't open**: Use the URL shown in terminal or try different port with `--port`

## Notes

- Always store refresh tokens in secret-vault
- Tokens can be revoked at https://myaccount.google.com/permissions
