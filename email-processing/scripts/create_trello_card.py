#!/usr/bin/env python3
"""
Create Trello card from email for tasks requiring >2 min work.
"""

import sys
import yaml
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta


def get_trello_credentials():
    """Retrieve Trello API credentials from Secret Manager."""
    api_key = subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest", "--secret=trello-api-key"],
        capture_output=True, text=True, check=True
    ).stdout.strip()

    token = subprocess.run(
        ["gcloud", "secrets", "versions", "access", "latest", "--secret=trello-token"],
        capture_output=True, text=True, check=True
    ).stdout.strip()

    return api_key, token


def get_boards(api_key, token):
    """Get all Trello boards."""
    result = subprocess.run(
        ["curl", "-s", f"https://api.trello.com/1/members/me/boards?key={api_key}&token={token}"],
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def get_lists(board_id, api_key, token):
    """Get all lists in a board."""
    result = subprocess.run(
        ["curl", "-s", f"https://api.trello.com/1/boards/{board_id}/lists?key={api_key}&token={token}"],
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)


def create_card(list_id, name, description, due_date, api_key, token):
    """Create a Trello card."""
    result = subprocess.run([
        "curl", "-s", "-X", "POST",
        f"https://api.trello.com/1/cards?key={api_key}&token={token}",
        "-d", f"idList={list_id}",
        "-d", f"name={name}",
        "-d", f"desc={description}",
        "-d", f"due={due_date}",
        "-d", "pos=top"
    ], capture_output=True, text=True, check=True)

    return json.loads(result.stdout)


def load_email(message_id):
    """Load email from most recent export."""
    triage_dir = Path.home() / "email_triage"
    yaml_files = sorted(triage_dir.glob("unread_emails_*.yaml"), reverse=True)

    if not yaml_files:
        print("❌ No email export files found in ~/email_triage")
        print("   Run: python3 export_unprocessed.py first")
        sys.exit(1)

    with open(yaml_files[0], 'r') as f:
        data = yaml.safe_load(f)

    emails = data.get('emails', [])

    for email in emails:
        if email['message_id'] == message_id:
            return email

    print(f"❌ Email with message_id '{message_id}' not found")
    sys.exit(1)


def format_card_description(email, action_notes):
    """Format Trello card description from email."""
    return f"""## Email Context
- **From**: {email['metadata']['from']}
- **Date**: {email['metadata']['date']}
- **Subject**: {email['metadata']['subject']}

## Original Message
{email['snippet']}

## Next Action
{action_notes}

---
_Created from email: {email['message_id']}_"""


def main():
    parser = argparse.ArgumentParser(
        description="Create Trello card from email"
    )
    parser.add_argument(
        "--message-id",
        required=True,
        help="Gmail message ID"
    )
    parser.add_argument(
        "--board",
        default="multifi",
        help="Trello board name (default: multifi)"
    )
    parser.add_argument(
        "--list",
        default="To Do",
        help="Trello list name (default: To Do)"
    )
    parser.add_argument(
        "--title",
        help="Card title (if not provided, will use email subject)"
    )
    parser.add_argument(
        "--action",
        help="Next action description"
    )
    parser.add_argument(
        "--due-days",
        type=int,
        default=1,
        help="Due date in days from now (default: 1)"
    )

    args = parser.parse_args()

    # Load email
    print(f"📧 Loading email: {args.message_id}")
    email = load_email(args.message_id)

    # Get Trello credentials
    print("🔐 Authenticating with Trello...")
    api_key, token = get_trello_credentials()

    # Find board
    print(f"📋 Finding board: {args.board}")
    boards = get_boards(api_key, token)
    board = next((b for b in boards if b['name'].lower() == args.board.lower()), None)

    if not board:
        print(f"❌ Board '{args.board}' not found")
        print("\nAvailable boards:")
        for b in boards:
            print(f"  - {b['name']}")
        sys.exit(1)

    # Find list
    print(f"📝 Finding list: {args.list}")
    lists = get_lists(board['id'], api_key, token)
    list_obj = next((l for l in lists if l['name'].lower() == args.list.lower()), None)

    if not list_obj:
        print(f"❌ List '{args.list}' not found in board '{args.board}'")
        print("\nAvailable lists:")
        for l in lists:
            print(f"  - {l['name']}")
        sys.exit(1)

    # Prepare card data
    card_title = args.title or email['metadata']['subject']
    action_notes = args.action or "Review and take appropriate action"

    # Calculate due date
    due_date = datetime.now() + timedelta(days=args.due_days)
    due_date_str = due_date.strftime("%Y-%m-%dT23:59:59.000Z")

    # Format description
    description = format_card_description(email, action_notes)

    # Create card
    print(f"✨ Creating Trello card...")
    card = create_card(list_obj['id'], card_title, description, due_date_str, api_key, token)

    print("\n" + "=" * 80)
    print("✅ Trello card created successfully!")
    print("=" * 80)
    print(f"\n📌 Title: {card['name']}")
    print(f"📅 Due: {due_date.strftime('%Y-%m-%d')}")
    print(f"🔗 URL: {card['shortUrl']}")
    print(f"\n💡 Next: Archive the email to clear your inbox")


if __name__ == "__main__":
    main()
