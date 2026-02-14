import sys
import argparse
from googleapiclient.discovery import build
from oauth_helper import get_credentials

def archive_message(service, message_id):
    """Archive a message by removing the INBOX label."""
    try:
        body = {
            "removeLabelIds": ["INBOX"]
        }
        service.users().messages().modify(userId="me", id=message_id, body=body).execute()
        print(f"✅ Archived message {message_id}")
    except Exception as e:
        print(f"❌ Error archiving message {message_id}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("message_ids", nargs="+", help="Message IDs to archive")
    parser.add_argument("--email", help="Email address to resolve secret name from")
    args = parser.parse_args()

    try:
        credentials = get_credentials(email_address=args.email)
        service = build("gmail", "v1", credentials=credentials)
        
        for mid in args.message_ids:
            archive_message(service, mid)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
