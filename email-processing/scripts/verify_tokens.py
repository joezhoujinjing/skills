#!/usr/bin/env python3
"""
Verify which Gmail accounts the tokens connect to.
"""

import sys
from pathlib import Path

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build


def check_token(token_name):
    """Check which Gmail account a token connects to."""
    try:
        print(f"\n{'='*60}")
        print(f"Checking token: {token_name}")
        print('='*60)

        credentials = get_credentials(refresh_token_secret=token_name)
        service = build("gmail", "v1", credentials=credentials)

        profile = service.users().getProfile(userId="me").execute()
        email = profile.get('emailAddress')

        print(f"✅ Connects to: {email}")

        # Get inbox count
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=1
        ).execute()
        inbox_count = results.get("resultSizeEstimate", 0)

        print(f"📬 Inbox count: {inbox_count}")

        return email

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    tokens = [
        "google-all-services-refresh-token-joezhoujinjing-gmail-com",
        "google-all-services-refresh-token-joe-multifi-ai"
    ]

    print("🔍 Verifying Gmail tokens...")

    for token in tokens:
        check_token(token)


if __name__ == "__main__":
    main()
