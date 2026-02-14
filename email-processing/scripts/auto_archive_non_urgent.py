import yaml
import sys
import os
from pathlib import Path
from googleapiclient.discovery import build

# Add the path to oauth_helper
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials

def main():
    # Load the most recent dump to identify newsletters/notifications/receipts
    triage_dir = Path.home() / "email_triage"
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)
    
    if not yaml_files:
        print("❌ No export files found.")
        return

    latest_file = yaml_files[0]
    print(f"📂 Loading from {latest_file.name}")
    with open(latest_file) as f:
        data = yaml.safe_load(f)
    
    emails = data.get('emails', [])
    to_archive = []
    
    # Define keywords for auto-archiving
    newsletter_domains = ['activityhero.com', 'substack.com', 'medium.com', 'beehiiv.com']
    notification_domains = ['discord.com', 'morganstanley.com', 'teamviewer.com', 'aliyun.com']
    
    for e in emails:
        from_addr = e['metadata']['from'].lower()
        subject = e['metadata']['subject'].lower()
        
        # Check for newsletters/notifications
        is_newsletter = any(domain in from_addr for domain in newsletter_domains)
        is_notification = any(domain in from_addr for domain in notification_domains)
        is_receipt = any(kw in subject for kw in ['receipt', 'invoice', 'payment confirmation', 'order confirmation', 'statement'])
        
        # Safety check: if it looks urgent, don't auto-archive
        is_urgent = any(kw in subject for kw in ['urgent', 'action required', 'past due', 'important'])
        
        if (is_newsletter or is_notification or is_receipt) and not is_urgent:
            to_archive.append(e)

    if not to_archive:
        print("✨ No low-priority emails found to archive.")
        return

    print(f"📦 Found {len(to_archive)} emails to archive:")
    for e in to_archive:
        print(f"  - {e['metadata']['subject'][:50]} (From: {e['metadata']['from'][:30]})")

    # Proceed to archive
    credentials = get_credentials()
    service = build("gmail", "v1", credentials=credentials)
    
    ids = [e['message_id'] for e in to_archive]
    body = {"ids": ids, "removeLabelIds": ["INBOX"]}
    
    try:
        service.users().messages().batchModify(userId="me", body=body).execute()
        print(f"✅ Successfully archived {len(to_archive)} emails.")
    except Exception as err:
        print(f"❌ Error archiving: {err}")

if __name__ == "__main__":
    main()
