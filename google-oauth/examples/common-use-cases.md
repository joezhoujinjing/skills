# Common Use Cases

## All Services (Recommended)

Full access to Gmail, Drive, Docs, Sheets, Slides, Calendar, Forms, and Chat:

```bash
/google-oauth get-token "https://mail.google.com/ https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/presentations https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/forms.body https://www.googleapis.com/auth/forms.responses.readonly https://www.googleapis.com/auth/chat.messages https://www.googleapis.com/auth/chat.spaces" --port 8085
```

Store the token:

```bash
/secret-vault set google-all-services-refresh-token-user@example.com "YOUR_TOKEN"
```

## Single Services

### Gmail

```bash
/google-oauth get-token "https://mail.google.com/" --port 8085
```

### Drive

```bash
/google-oauth get-token "https://www.googleapis.com/auth/drive" --port 8085
```

### Calendar

```bash
/google-oauth get-token "https://www.googleapis.com/auth/calendar" --port 8085
```

## Service Combinations

### Gmail + Drive + Calendar

```bash
/google-oauth get-token "https://mail.google.com/ https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/calendar" --port 8085
```

### Google Workspace (Docs, Sheets, Slides)

```bash
/google-oauth get-token "https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/presentations" --port 8085
```

## Setup Checklist

Before running:

1. ✅ Add `http://localhost:8085/` to OAuth client redirect URIs
2. ✅ Enable required APIs in Google Cloud Console
3. ✅ Configure OAuth consent screen with required scopes

After getting token:

1. Store in secret-vault with email identifier
2. Test the token with a simple API call
3. Document which scopes were authorized
