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
    review_file = Path("data/emails_to_review.yaml")
    if not review_file.exists():
        print("No review file found.")
        return

    with open(review_file) as f:
        data = yaml.safe_load(f)
    
    # Extract IDs
    ids = [item['message_id'] for item in data['emails_needing_review']]
    
    if not ids:
        print("No emails to archive.")
        return
        
    print(f"Found {len(ids)} emails to archive.")
    
    credentials = get_credentials()
    service = build("gmail", "v1", credentials=credentials)
    
    batch_archive(service, ids)
    print("✅ Done.")

if __name__ == "__main__":
    main()
