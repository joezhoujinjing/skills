#!/usr/bin/env python3
"""
Batch archive emails by category.
"""

import sys
import yaml
import time
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials


CATEGORY_PATTERNS = {
    'newsletters': [
        'substack.com', 'medium.com', 'beehiiv.com', 'convertkit.com',
        'mailchi.mp', 'newsletter'
    ],
    'social_notifications': [
        'linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com'
    ],
    'receipts': [
        'receipt', 'invoice', 'payment confirmation', 'order confirmation'
    ],
}


def categorize_email(email):
    """Check which categories an email belongs to."""
    from_addr = email['metadata']['from'].lower()
    subject = email['metadata']['subject'].lower()

    categories = []

    # Check newsletters
    if any(pattern in from_addr or pattern in subject
           for pattern in CATEGORY_PATTERNS['newsletters']):
        # Exclude direct messages from LinkedIn
        if 'linkedin.com' in from_addr and 'message' not in subject:
            categories.append('newsletters')
        elif 'linkedin.com' not in from_addr:
            categories.append('newsletters')

    # Check social notifications
    if any(pattern in from_addr for pattern in CATEGORY_PATTERNS['social_notifications']):
        if 'message' not in subject and 'invitation' not in subject:
            categories.append('social_notifications')

    # Check receipts
    if any(pattern in subject for pattern in CATEGORY_PATTERNS['receipts']):
        categories.append('receipts')

    return categories


def batch_archive(service, message_ids, batch_size=100):
    """Archive messages in batches."""
    total = len(message_ids)
    archived = 0

    print(f"\n📦 Archiving {total} messages...")

    for i in range(0, total, batch_size):
        batch = message_ids[i:i + batch_size]

        try:
            progress = (i + len(batch)) / total * 100
            print(f"   Progress: {i + len(batch)}/{total} ({progress:.1f}%)", end="\r")

            body = {
                "ids": batch,
                "removeLabelIds": ["INBOX"]
            }

            service.users().messages().batchModify(
                userId="me",
                body=body
            ).execute()

            archived += len(batch)
            time.sleep(0.1)

        except HttpError as e:
            print(f"\n⚠️  Error archiving batch: {e}")
            continue

    print(f"\n✅ Archived {archived}/{total} messages")
    return archived


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_archive_by_category.py <category>")
        print("\nAvailable categories:")
        print("  - newsletters")
        print("  - social_notifications")
        print("  - receipts")
        print("\nExample:")
        print("  python batch_archive_by_category.py newsletters")
        sys.exit(1)

    category = sys.argv[1]

    if category not in CATEGORY_PATTERNS:
        print(f"❌ Unknown category: {category}")
        print(f"   Available: {', '.join(CATEGORY_PATTERNS.keys())}")
        sys.exit(1)

    # Load most recent email export
    triage_dir = Path.home() / "email_triage"
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)

    if not yaml_files:
        print("❌ No email export files found")
        sys.exit(1)

    print(f"📂 Loading emails from: {yaml_files[0].name}")
    with open(yaml_files[0], 'r') as f:
        data = yaml.safe_load(f)

    emails = data.get('emails', [])

    # Filter by category
    to_archive = []
    for email in emails:
        cats = categorize_email(email)
        if category in cats:
            to_archive.append(email)

    if not to_archive:
        print(f"\n✨ No emails found in category '{category}'")
        return

    print(f"\n📧 Found {len(to_archive)} emails in category '{category}'")
    print("\nSample emails:")
    for i, email in enumerate(to_archive[:5], 1):
        print(f"  {i}. From: {email['metadata']['from'][:50]}")
        print(f"     Subject: {email['metadata']['subject'][:60]}")

    if len(to_archive) > 5:
        print(f"  ... and {len(to_archive) - 5} more")

    # Confirm
    response = input(f"\n⚠️  Archive all {len(to_archive)} '{category}' emails? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        return

    # Archive
    print("🔐 Authenticating with Gmail...")
    credentials = get_credentials()
    service = build("gmail", "v1", credentials=credentials)

    message_ids = [email['message_id'] for email in to_archive]
    archived = batch_archive(service, message_ids)

    print(f"\n🎉 Done! Archived {archived} emails in category '{category}'")


if __name__ == "__main__":
    main()
