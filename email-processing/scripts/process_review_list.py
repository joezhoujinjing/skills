#!/usr/bin/env python3
"""
Process the review list remotely via Claude Code.
Presents emails needing review with suggested actions for Claude to help with.
"""

import yaml
import sys
from pathlib import Path
import subprocess


def load_review_list():
    """Load emails needing review."""
    skill_dir = Path(__file__).parent.parent
    review_file = skill_dir / "data" / "emails_to_review.yaml"

    if not review_file.exists():
        print("✅ No emails to review!")
        return []

    with open(review_file, 'r') as f:
        data = yaml.safe_load(f)

    return data.get('emails_needing_review', [])


def archive_email(message_id):
    """Archive email."""
    try:
        subprocess.run(
            ['python', 'batch_archive_remaining.py', '--message-ids', message_id],
            cwd=Path(__file__).parent,
            check=True,
            capture_output=True
        )
        return True
    except Exception as e:
        print(f"❌ Failed to archive: {e}")
        return False


def send_reply(message_id, body):
    """Send reply to email."""
    try:
        subprocess.run(
            ['python', 'send_reply.py', '--message-id', message_id, '--body', body],
            cwd=Path(__file__).parent,
            check=True
        )
        return True
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")
        return False


def create_trello_card(message_id, action, due_days=1, title=None):
    """Create Trello card from email."""
    try:
        cmd = [
            'python', 'create_trello_card.py',
            '--message-id', message_id,
            '--action', action,
            '--due-days', str(due_days)
        ]

        if title:
            cmd.extend(['--title', title])

        subprocess.run(cmd, cwd=Path(__file__).parent, check=True)
        return True
    except Exception as e:
        print(f"❌ Failed to create Trello card: {e}")
        return False


def display_email_for_review(email, index, total):
    """Display email details for Claude to review."""
    print("\n" + "=" * 80)
    print(f"📧 Email {index}/{total} — {email['category'].upper()}")
    print("=" * 80)
    print(f"Message ID: {email['message_id']}")
    print(f"From: {email['from']}")
    print(f"Subject: {email['subject']}")
    print(f"Date: {email['date']}")
    print("-" * 80)
    print(f"Snippet:\n{email['snippet']}")
    print("-" * 80)
    print(f"Reason: {email['reason']}")
    print()

    if email.get('suggested_actions'):
        print("💡 Suggested Actions:")
        for i, suggestion in enumerate(email['suggested_actions'], 1):
            print(f"   {i}. {suggestion['action']} (due in {suggestion['due_days']} days)")
        print()


def main():
    """Main review processing."""
    print("=" * 80)
    print("📋 REVIEW LIST PROCESSOR")
    print("=" * 80)

    emails = load_review_list()

    if not emails:
        print("✅ No emails to review!")
        return

    print(f"\n📊 {len(emails)} emails need your attention\n")
    print("This script will present each email for you to decide:")
    print("  - Archive with no action")
    print("  - Send a quick reply")
    print("  - Create a Trello card")
    print()

    for i, email in enumerate(emails, 1):
        display_email_for_review(email, i, len(emails))

        print("Available commands:")
        print("  archive              - Archive without action")
        print("  reply: <message>     - Send quick reply and archive")
        print("  trello: <action>     - Create Trello card and archive")
        print("  skip                 - Skip for now")
        print("  quit                 - Exit review session")
        print()

        choice = input("Command: ").strip()

        if choice.lower() == 'quit':
            print("\n🛑 Exiting review session")
            break
        elif choice.lower() == 'skip':
            print("⏭️  Skipped")
            continue
        elif choice.lower() == 'archive':
            print("📁 Archiving...")
            if archive_email(email['message_id']):
                print("✅ Archived!")
        elif choice.lower().startswith('reply:'):
            body = choice[6:].strip()
            if body:
                print(f"📤 Sending reply: {body[:50]}...")
                if send_reply(email['message_id'], body):
                    print("✅ Reply sent!")
                    archive_email(email['message_id'])
            else:
                print("❌ No reply body provided")
        elif choice.lower().startswith('trello:'):
            action = choice[7:].strip()
            if action:
                print(f"📋 Creating Trello card: {action[:50]}...")
                if create_trello_card(email['message_id'], action):
                    print("✅ Trello card created!")
                    archive_email(email['message_id'])
            else:
                # Use first suggested action
                if email.get('suggested_actions'):
                    action = email['suggested_actions'][0]['action']
                    due_days = email['suggested_actions'][0]['due_days']
                    print(f"📋 Creating Trello card with suggested action...")
                    if create_trello_card(email['message_id'], action, due_days):
                        print("✅ Trello card created!")
                        archive_email(email['message_id'])
                else:
                    print("❌ No action provided and no suggestions available")

    print("\n" + "=" * 80)
    print("✅ Review session complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
