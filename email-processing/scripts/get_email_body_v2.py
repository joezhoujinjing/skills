import argparse
import sys
import base64
from pathlib import Path

# Import from google-services skill (adjusting path if needed)
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build

def get_message_body(service, msg_id):
    msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg.get('payload', {})
    
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

    if 'parts' in payload:
        body = parse_parts(payload['parts'])
    else:
        data = payload.get('body', {}).get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode()
        else:
            body = ""
    return body

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("message_id")
    args = parser.parse_args()
    
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    print(get_message_body(service, args.message_id))

if __name__ == "__main__":
    main()
