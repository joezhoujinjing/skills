#!/usr/bin/env python3
"""
Check inbox count for Gmail account.
"""

import sys
from pathlib import Path

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build


def get_full_count(service, label_id):
    """
    Get accurate count by fetching the label details.
    """
    label = service.users().labels().get(userId="me", id=label_id).execute()
    return label.get("messagesTotal", 0)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Check inbox count"
    )
    parser.add_argument(
        "--refresh-token-secret",
        help="Secret name for Gmail refresh token"
    )

    args = parser.parse_args()

    print("🔐 Authenticating with Gmail...")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    print("📧 Building Gmail service...")
    service = build("gmail", "v1", credentials=credentials)

    # Get profile
    profile = service.users().getProfile(userId="me").execute()
    print(f"\n📊 Account: {profile.get('emailAddress')}")

    # 1. Inbox Total: All messages in the INBOX label (read or unread).
    # Using labels.get is accurate and does not use resultSizeEstimate.
    inbox_total = get_full_count(service, "INBOX")

    # 2. Total Unread: All messages with the UNREAD label across the entire account.
    total_unread = get_full_count(service, "UNREAD")

    print(f"📬 Inbox Total: {inbox_total}")
    print(f"📭 Total Unread: {total_unread}")


if __name__ == "__main__":
    main()
