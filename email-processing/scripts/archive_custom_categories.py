import yaml
import sys
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials

# Categories definition based on user request
CATEGORIES = {
    'social_newsletter': [
        'linkedin.com', 'substack.com', 'medium.com', 'beehiiv.com', 
        'convertkit.com', 'twitter.com', 'facebook.com', 'instagram.com',
        'social', 'newsletter', 'digest'
    ],
    'saas_notifications': [
        'vanta.com', 'fireflies.ai', 'slack.com', 'claude.com', 'anthropic.com',
        'openai.com', 'github.com', 'gitlab.com', 'linear.app', 'notion.so',
        'trello.com', 'asana.com', 'atlassian.com', 'jira', 'confluence',
        'zoom.us', 'google.com', 'aws.amazon.com', 'sentry.io', 'datadoghq.com',
        'pagerduty.com', 'stripe.com', 'mercury.com', 'rippling.com', 'gusto.com',
        'bill.com', 'expensify.com', 'brex.com', 'ramp.com', 'pilot.com'
    ]
}

def is_match(email, keywords):
    """Check if email matches any keyword in sender or subject."""
    sender = email['metadata']['from'].lower()
    subject = email['metadata']['subject'].lower()
    
    for keyword in keywords:
        if keyword in sender:
            return True
        # Only check subject if it's a very specific keyword, otherwise too risky
        if keyword in subject and len(keyword) > 5:
            return True
    return False

def batch_archive(service, message_ids, batch_size=100):
    total = len(message_ids)
    print(f"📦 Archiving {total} messages...")
    
    archived_count = 0
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
            archived_count += len(batch)
            print(f"   Batch {i//batch_size + 1} done ({len(batch)} emails)")
        except Exception as e:
            print(f"   Error in batch: {e}")
    return archived_count

def main():
    # Find most recent export file
    triage_dir = Path.home() / "email_triage"
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)

    if not yaml_files:
        print("❌ No email export files found.")
        return

    yaml_file = yaml_files[0]
    print(f"📂 Loading emails from: {yaml_file.name}")

    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    all_emails = data.get('emails', [])
    to_archive = []
    
    print(f"🔍 Scanning {len(all_emails)} emails...")

    for email in all_emails:
        # Check Social/Newsletter
        if is_match(email, CATEGORIES['social_newsletter']):
            to_archive.append(email)
            continue # Don't add twice
        
        # Check SaaS/Notifications
        if is_match(email, CATEGORIES['saas_notifications']):
            to_archive.append(email)
            continue

    if not to_archive:
        print("✨ No matching emails found to archive.")
        return

    print(f"\n📧 Found {len(to_archive)} emails matching 'Social/Newsletter' or 'SaaS Notifications'.")
    print("Sample matches:")
    for e in to_archive[:5]:
        print(f"  - {e['metadata']['from']} | {e['metadata']['subject'][:50]}...")
    
    confirm = input(f"\n⚠️  Archive these {len(to_archive)} emails? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled.")
        return

    print("🔐 Authenticating...")
    # Use the token for joe@multifi.ai (passed via env or args usually, but here hardcoded/default)
    # The previous export used a specific token secret. We need to reuse that.
    # We'll rely on the default credential flow which should pick up the active token or we might need to specify.
    # Actually, the user context switched to joe@multifi.ai for the export, so we should be careful.
    # The script `oauth_helper` usually picks up `google-all-services-refresh-token`.
    # We need to ensure we use `google-all-services-refresh-token-joe-multifi-ai`.
    
    # Simple hack: check if we can pass it, or just let oauth_helper handle it if configured.
    # Since I cannot easily pass args to get_credentials in this script without modifying it to accept args,
    # I will modify get_credentials call below to use the specific secret if I can.
    # But for now, let's assume I can pass it as an argument or it defaults to the last used?
    # No, oauth_helper defaults to `google-all-services-refresh-token` (the main one).
    # I need to explicitly use the multifi one.
    
    credentials = get_credentials(refresh_token_secret="google-all-services-refresh-token-joe-multifi-ai")
    service = build("gmail", "v1", credentials=credentials)
    
    ids = [e['message_id'] for e in to_archive]
    batch_archive(service, ids)
    print("\n✅ Done.")

if __name__ == "__main__":
    main()
