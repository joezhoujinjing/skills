import yaml
import sys
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials

def batch_archive(service, message_ids, batch_size=100):
    total = len(message_ids)
    print(f"📦 Archiving {total} messages...")
    
    for i in range(0, total, batch_size):
        batch = message_ids[i:i + batch_size]
        try:
            body = {
                "ids": batch,
                "removeLabelIds": ["INBOX"]
            }
            service.users().messages().batchModify(
                userId="me",
                body=body
            ).execute()
            print(f"   Batch {i//batch_size + 1} done ({len(batch)} emails)")
        except Exception as e:
            print(f"   Error in batch: {e}")

def main():
    triage_dir = Path.home() / "email_triage"
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)
    
    if not yaml_files:
        print("No export found.")
        return

    with open(yaml_files[0]) as f:
        data = yaml.safe_load(f)
    
    # We want to archive EVERYTHING in the current dump EXCEPT maybe the ones we just processed as Trello cards?
    # But those are effectively processed too (user said "archive the rest").
    # The Trello card creation step *does* offer to archive but we didn't take it (script ended).
    # So we should archive ALL 121 emails in the current dump.
    
    ids = [e['message_id'] for e in data.get('emails', [])]
    
    if not ids:
        print("No emails to archive.")
        return
        
    print(f"Found {len(ids)} remaining emails (Financial, Calendar, DMs, etc.). Archiving ALL.")
    
    credentials = get_credentials(refresh_token_secret="google-all-services-refresh-token-joe-multifi-ai")
    service = build("gmail", "v1", credentials=credentials)
    
    batch_archive(service, ids)
    print("✅ Done.")

if __name__ == "__main__":
    main()
