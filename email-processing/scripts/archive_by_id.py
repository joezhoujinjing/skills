import argparse
import sys
from pathlib import Path

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build

def archive_message(service, msg_id):
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={
                'removeLabelIds': ['INBOX', 'UNREAD']
            }
        ).execute()
        return True
    except Exception as e:
        print(f"Error archiving {msg_id}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("message_ids", nargs='+')
    args = parser.parse_args()
    
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    
    for mid in args.message_ids:
        if archive_message(service, mid):
            print(f"Successfully archived {mid}")
        else:
            print(f"Failed to archive {mid}")

if __name__ == "__main__":
    main()
