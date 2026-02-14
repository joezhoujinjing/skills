import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    creds = None
    token_path = os.path.expanduser('~/openclaw/skills/email-processing/token.json')
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("No valid credentials found.")
    return build('gmail', 'v1', credentials=creds)

def get_message_body(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg.get('payload', {})
    parts = payload.get('parts', [])
    
    def parse_parts(parts):
        body = ""
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body += base64.urlsafe_b64decode(data).decode()
            elif 'parts' in part:
                body += parse_parts(part['parts'])
        return body

    body = parse_parts(parts)
    if not body and 'body' in payload:
        data = payload['body'].get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode()
    return body

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 get_email_body.py <message_id>")
        sys.exit(1)
    service = get_service()
    print(get_message_body(service, sys.argv[1]))
