#!/usr/bin/env python3
"""
Batch archive remaining safe-to-archive emails.
"""

import sys
import yaml
import time
from pathlib import Path
from googleapiclient.discovery import build

sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials


def should_archive(email):
    """Determine if email should be auto-archived."""
    from_addr = email['metadata']['from'].lower()
    subject = email['metadata']['subject'].lower()
    date = email['metadata']['date']

    # Fireflies.ai summaries
    if 'fireflies.ai' in from_addr:
        return ('fireflies', f"Fireflies: {subject[:50]}")

    # Slack digests
    if 'slack.com' in from_addr and ('digest' in subject or 'unread' in subject):
        return ('slack_digest', f"Slack: {subject[:50]}")

    # Anthropic updates (non-receipts)
    if 'anthropic.com' in from_addr or 'claude.com' in from_addr:
        if 'receipt' not in subject and 'invoice' not in subject:
            return ('anthropic_updates', f"Anthropic: {subject[:50]}")

    # Supabase updates
    if 'supabase' in from_addr:
        return ('supabase', f"Supabase: {subject[:50]}")

    # Rippling updates
    if 'rippling.com' in from_addr:
        return ('rippling', f"Rippling: {subject[:50]}")

    # Vanta notifications (non-urgent)
    if 'vanta.com' in from_addr:
        if 'action' not in subject and 'urgent' not in subject:
            return ('vanta_info', f"Vanta: {subject[:50]}")

    # Plaid notifications
    if 'plaid.com' in from_addr:
        return ('plaid', f"Plaid: {subject[:50]}")

    # Mercury notifications (non-receipts)
    if 'mercury.com' in from_addr:
        if 'receipt' not in subject and 'invoice' not in subject and 'payment' not in subject:
            return ('mercury_updates', f"Mercury: {subject[:50]}")

    # Bill.com updates
    if 'bill.com' in from_addr:
        return ('bill_com', f"Bill.com: {subject[:50]}")

    # Stripe notifications (non-receipts)
    if 'stripe.com' in from_addr:
        if 'receipt' not in subject and 'invoice' not in subject:
            return ('stripe_updates', f"Stripe: {subject[:50]}")

    # Trello notifications
    if 'trello.com' in from_addr:
        return ('trello', f"Trello: {subject[:50]}")

    # Google Calendar past events
    if 'calendar' in from_addr or 'google.com' in from_addr:
        if 'invitation' in subject or 'updated' in subject or 'canceled' in subject:
            return ('calendar', f"Calendar: {subject[:50]}")

    # AWS notifications
    if 'aws' in from_addr or 'amazon' in from_addr:
        return ('aws', f"AWS: {subject[:50]}")

    return None


def batch_archive(service, message_ids, batch_size=100):
    """Archive messages in batches."""
    total = len(message_ids)
    archived = 0

    for i in range(0, total, batch_size):
        batch = message_ids[i:i + batch_size]

        try:
            progress = min(i + len(batch), total)
            print(f"   Progress: {progress}/{total} ({progress/total*100:.1f}%)", end="\r")

            body = {
                "ids": batch,
                "removeLabelIds": ["INBOX", "UNREAD"]
            }

            service.users().messages().batchModify(
                userId="me",
                body=body
            ).execute()

            archived += len(batch)
            time.sleep(0.1)

        except Exception as e:
            print(f"\n⚠️  Error archiving batch: {e}")
            continue

    print(f"\n✅ Archived {archived}/{total} messages")
    return archived


def main():
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

    # Categorize emails
    to_archive = {}

    for email in emails:
        result = should_archive(email)
        if result:
            category, desc = result
            if category not in to_archive:
                to_archive[category] = []
            to_archive[category].append((email['message_id'], desc))

    if not to_archive:
        print("\n✨ No emails found to batch archive")
        return

    # Print summary
    print("\n" + "=" * 80)
    print("📦 EMAILS TO BATCH ARCHIVE")
    print("=" * 80)

    total_count = 0
    for category, emails_list in sorted(to_archive.items()):
        print(f"\n🏷️  {category.upper().replace('_', ' ')} ({len(emails_list)} emails)")
        for msg_id, desc in emails_list[:3]:
            print(f"   - {desc}")
        if len(emails_list) > 3:
            print(f"   ... and {len(emails_list) - 3} more")
        total_count += len(emails_list)

    print("\n" + "=" * 80)
    print(f"📊 TOTAL: {total_count} emails will be archived")
    print("=" * 80)

    # Confirm
    response = input("\n⚠️  Archive all these emails? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        return

    # Archive
    print("\n🔐 Authenticating with Gmail...")
    credentials = get_credentials()
    service = build("gmail", "v1", credentials=credentials)

    all_message_ids = []
    for category, emails_list in to_archive.items():
        all_message_ids.extend([msg_id for msg_id, _ in emails_list])

    print(f"\n📦 Archiving {len(all_message_ids)} messages...")
    archived = batch_archive(service, all_message_ids)

    print(f"\n🎉 Done! Archived {archived} emails")
    print(f"   Categories processed: {', '.join(to_archive.keys())}")


if __name__ == "__main__":
    main()
