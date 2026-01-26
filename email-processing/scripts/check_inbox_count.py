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

    # Check inbox
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=1
    ).execute()

    inbox_count = results.get("resultSizeEstimate", 0)

    print(f"📬 Emails in INBOX: {inbox_count}")

    # Check unread
    results = service.users().messages().list(
        userId="me",
        q="is:unread",
        maxResults=1
    ).execute()

    unread_count = results.get("resultSizeEstimate", 0)

    print(f"📭 Unread emails (any location): {unread_count}")

    # Check unread in inbox
    results = service.users().messages().list(
        userId="me",
        q="is:unread in:inbox",
        maxResults=1
    ).execute()

    unread_inbox_count = results.get("resultSizeEstimate", 0)

    print(f"📬 Unread in INBOX: {unread_inbox_count}")


if __name__ == "__main__":
    main()
