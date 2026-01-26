#!/usr/bin/env python3
"""
Interactive email processing workflow with GTD principles.
Walks through each email with options: no reply, quick reply, or create Trello card.
"""

import yaml
import sys
from pathlib import Path
from datetime import datetime
import subprocess


def load_emails():
    """Load emails from the dump file."""
    skill_dir = Path(__file__).parent.parent
    dump_file = skill_dir / "data" / "emails_dump.yaml"

    if not dump_file.exists():
        print("❌ No data/emails_dump.yaml found!")
        print("   Run: python export_unprocessed.py first")
        sys.exit(1)

    with open(dump_file, 'r') as f:
        data = yaml.safe_load(f)

    return data.get('emails', [])


def categorize_email(email):
    """Categorize email for priority ordering."""
    subject = email['metadata']['subject'].lower()
    from_addr = email['metadata']['from'].lower()

    # Priority levels
    if any(keyword in subject for keyword in ['action required', 'urgent', 'approve', 'deadline']):
        return 'urgent', 0

    if 'multifi.ai' in from_addr:
        return 'internal', 1

    if 'linkedin.com' in from_addr and 'message' in subject:
        return 'direct_message', 2

    if any(d in from_addr for d in ['linkedin.com', 'calendar']):
        return 'direct_message', 2

    if any(d in from_addr for d in ['substack.com', 'medium.com', 'beehiiv.com']):
        return 'newsletter', 4

    return 'other', 3


def sort_emails_by_priority(emails):
    """Sort emails by priority (urgent first)."""
    categorized = []
    for email in emails:
        category, priority = categorize_email(email)
        categorized.append((priority, category, email))

    categorized.sort(key=lambda x: x[0])
    return categorized


def print_email_details(email, index, total, category):
    """Print email details in a readable format."""
    print("\n" + "=" * 80)
    print(f"📧 Email {index}/{total} — Category: {category.upper()}")
    print("=" * 80)
    print(f"From: {email['metadata']['from']}")
    print(f"Subject: {email['metadata']['subject']}")
    print(f"Date: {email['metadata']['date']}")
    print(f"Message ID: {email['message_id']}")
    print("-" * 80)
    print(f"Snippet: {email['snippet'][:200]}")
    print("=" * 80)


def get_user_choice():
    """Get user's processing decision."""
    print("\nHow do you want to process this email?")
    print("  a) No reply needed (archive)")
    print("  b) Quick reply (<2 min)")
    print("  c) Create Trello card (>2 min work)")
    print("  s) Skip for now")
    print("  q) Quit processing")

    while True:
        choice = input("\nChoice [a/b/c/s/q]: ").lower().strip()
        if choice in ['a', 'b', 'c', 's', 'q']:
            return choice
        print("❌ Invalid choice. Please enter a, b, c, s, or q")


def archive_email(message_id):
    """Archive email via gmail API."""
    try:
        # Call the batch archive script
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


def quick_reply(message_id):
    """Handle quick reply workflow."""
    print("\n" + "-" * 80)
    print("Quick Reply Mode")
    print("-" * 80)

    body = input("Enter your reply (or press Enter to cancel): ").strip()

    if not body:
        print("❌ Reply cancelled")
        return False

    try:
        subprocess.run(
            ['python', 'send_reply.py', '--message-id', message_id, '--body', body],
            cwd=Path(__file__).parent,
            check=True
        )
        print("✅ Reply sent!")

        # Archive after replying
        archive_email(message_id)
        return True
    except Exception as e:
        print(f"❌ Failed to send reply: {e}")
        return False


def create_trello_card(email):
    """Handle Trello card creation workflow."""
    print("\n" + "-" * 80)
    print("Create Trello Card Mode")
    print("-" * 80)

    # Suggest default action
    subject = email['metadata']['subject']
    suggested_action = f"Review and respond to: {subject}"

    print(f"\nSuggested action: {suggested_action}")
    action = input("Enter action description (or press Enter to use suggestion): ").strip()

    if not action:
        action = suggested_action

    # Optional: custom title
    use_custom_title = input("Use custom card title? [y/N]: ").lower().strip() == 'y'
    title_arg = []

    if use_custom_title:
        title = input("Enter card title: ").strip()
        if title:
            title_arg = ['--title', title]

    # Optional: due date
    due_days = input("Due in how many days? [1]: ").strip()
    due_days = due_days if due_days else "1"

    try:
        cmd = [
            'python', 'create_trello_card.py',
            '--message-id', email['message_id'],
            '--action', action,
            '--due-days', due_days
        ] + title_arg

        subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            check=True
        )
        print("✅ Trello card created!")

        # Archive after creating card
        archive_email(email['message_id'])
        return True
    except Exception as e:
        print(f"❌ Failed to create Trello card: {e}")
        return False


def main():
    """Main interactive processing loop."""
    print("=" * 80)
    print("📬 INTERACTIVE EMAIL PROCESSING")
    print("=" * 80)
    print("\nLoading emails...")

    emails = load_emails()

    if not emails:
        print("✨ No emails to process!")
        return

    print(f"✅ Loaded {len(emails)} emails")
    print("\n📊 Sorting by priority (urgent → direct messages → others)...")

    sorted_emails = sort_emails_by_priority(emails)

    # Stats
    stats = {
        'processed': 0,
        'archived': 0,
        'replied': 0,
        'trello': 0,
        'skipped': 0
    }

    for i, (priority, category, email) in enumerate(sorted_emails, 1):
        print_email_details(email, i, len(sorted_emails), category)

        choice = get_user_choice()

        if choice == 'q':
            print("\n🛑 Quitting processing session")
            break
        elif choice == 's':
            print("⏭️  Skipped")
            stats['skipped'] += 1
            continue
        elif choice == 'a':
            print("\n📁 Archiving email...")
            if archive_email(email['message_id']):
                print("✅ Archived!")
                stats['archived'] += 1
                stats['processed'] += 1
        elif choice == 'b':
            if quick_reply(email['message_id']):
                stats['replied'] += 1
                stats['processed'] += 1
        elif choice == 'c':
            if create_trello_card(email):
                stats['trello'] += 1
                stats['processed'] += 1

    # Final summary
    print("\n" + "=" * 80)
    print("📊 PROCESSING SUMMARY")
    print("=" * 80)
    print(f"  Total emails: {len(sorted_emails)}")
    print(f"  ✅ Processed: {stats['processed']}")
    print(f"     - Archived: {stats['archived']}")
    print(f"     - Replied: {stats['replied']}")
    print(f"     - Trello cards: {stats['trello']}")
    print(f"  ⏭️  Skipped: {stats['skipped']}")
    print(f"  📮 Remaining: {len(sorted_emails) - stats['processed']}")
    print("=" * 80)

    if stats['processed'] == len(sorted_emails):
        print("\n🎉 INBOX ZERO ACHIEVED! 🎉")
        print("✨ All emails processed successfully!")
    else:
        print(f"\n💪 Great progress! {len(sorted_emails) - stats['processed']} emails left.")
        print("   Run this script again to continue processing.")

    print("\n💡 Next step: Run `python export_unprocessed.py --verify` to confirm inbox zero")


if __name__ == "__main__":
    main()
