#!/usr/bin/env python3
"""
Show urgent/action-required emails that need immediate attention.
"""

import yaml
from pathlib import Path
from datetime import datetime


def is_urgent(email):
    """Check if email requires urgent action."""
    subject = email['metadata']['subject'].lower()
    from_addr = email['metadata']['from'].lower()

    urgent_keywords = [
        'action required', 'urgent', 'approve', 'approval needed',
        'confirm', 'verification', 'expiring', 'expires',
        'deadline', 'due', 'overdue', 'final notice'
    ]

    # Check subject
    if any(keyword in subject for keyword in urgent_keywords):
        return True

    # Important senders
    if 'multifi.ai' in from_addr:
        return True

    # Specific patterns
    if 'vanta.com' in from_addr and 'risk' in subject:
        return True

    if 'stripe.com' in from_addr and any(w in subject for w in ['failed', 'declined', 'action']):
        return True

    return False


def is_direct_message(email):
    """Check if it's a direct message from a person."""
    subject = email['metadata']['subject'].lower()
    from_addr = email['metadata']['from'].lower()

    if 'linkedin.com' in from_addr and 'sent you a message' in subject:
        return True

    # Calendar invites from real people
    if 'calendar' in from_addr or 'invitation' in subject:
        # Exclude automated ones
        if not any(noreply in from_addr for noreply in ['noreply', 'no-reply', 'donotreply']):
            return True

    return False


def main():
    # Load most recent export
    triage_dir = Path.home() / "email_triage"
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)

    if not yaml_files:
        print("❌ No email export files found")
        return

    print(f"📂 Loading emails from: {yaml_files[0].name}\n")
    with open(yaml_files[0], 'r') as f:
        data = yaml.safe_load(f)

    emails = data.get('emails', [])

    # Categorize
    urgent_emails = []
    direct_messages = []
    other_emails = []

    for email in emails:
        if is_urgent(email):
            urgent_emails.append(email)
        elif is_direct_message(email):
            direct_messages.append(email)
        else:
            other_emails.append(email)

    print("=" * 80)
    print("🔴 URGENT EMAILS (Action Required)")
    print("=" * 80)

    if urgent_emails:
        for i, email in enumerate(urgent_emails, 1):
            print(f"\n{i}. From: {email['metadata']['from']}")
            print(f"   Subject: {email['metadata']['subject']}")
            print(f"   Date: {email['metadata']['date']}")
            print(f"   Snippet: {email['snippet'][:100]}...")
    else:
        print("\n✅ No urgent emails found!")

    print("\n" + "=" * 80)
    print("💬 DIRECT MESSAGES (From People)")
    print("=" * 80)

    if direct_messages:
        for i, email in enumerate(direct_messages, 1):
            print(f"\n{i}. From: {email['metadata']['from']}")
            print(f"   Subject: {email['metadata']['subject']}")
            print(f"   Date: {email['metadata']['date']}")
    else:
        print("\n✅ No direct messages found!")

    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"  🔴 Urgent: {len(urgent_emails)}")
    print(f"  💬 Direct Messages: {len(direct_messages)}")
    print(f"  📧 Other: {len(other_emails)}")
    print(f"  📮 Total: {len(emails)}")
    print()


if __name__ == "__main__":
    main()
