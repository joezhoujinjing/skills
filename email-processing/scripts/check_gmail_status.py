#!/usr/bin/env python3
"""
Check Gmail account status and email distribution.
"""

import sys
from pathlib import Path

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build


def main():
    print("🔐 Authenticating with Gmail...")
    credentials = get_credentials()

    print("📧 Building Gmail service...")
    service = build("gmail", "v1", credentials=credentials)

    # Get profile info
    print("\n" + "=" * 80)
    print("📊 GMAIL ACCOUNT STATUS")
    print("=" * 80)

    profile = service.users().getProfile(userId="me").execute()
    print(f"\nEmail Address: {profile.get('emailAddress')}")
    print(f"Total Messages: {profile.get('messagesTotal')}")
    print(f"Total Threads: {profile.get('threadsTotal')}")

    # Get all labels
    print("\n" + "=" * 80)
    print("📁 LABELS AND MESSAGE COUNTS")
    print("=" * 80)

    labels_result = service.users().labels().list(userId="me").execute()
    labels = labels_result.get("labels", [])

    # Sort by message count
    label_counts = []
    for label in labels:
        name = label.get("name", "")
        msg_total = label.get("messagesTotal", 0)
        msg_unread = label.get("messagesUnread", 0)

        if msg_total > 0:  # Only show labels with messages
            label_counts.append((name, msg_total, msg_unread))

    label_counts.sort(key=lambda x: x[1], reverse=True)

    print(f"\n{'Label':<30} {'Total':<10} {'Unread':<10}")
    print("-" * 50)
    for name, total, unread in label_counts:
        print(f"{name:<30} {total:<10} {unread:<10}")

    # Check specific important labels
    print("\n" + "=" * 80)
    print("🔍 CHECKING KEY LOCATIONS")
    print("=" * 80)

    queries = {
        "INBOX": "in:inbox",
        "All Mail": "in:anywhere",
        "Unread": "is:unread",
        "Important": "is:important",
        "Starred": "is:starred",
    }

    for label, query in queries.items():
        try:
            result = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=1
            ).execute()

            count = result.get("resultSizeEstimate", 0)
            print(f"\n{label}: {count} emails")

            # Show first email if exists
            if count > 0:
                messages = result.get("messages", [])
                if messages:
                    msg_id = messages[0]["id"]
                    message = service.users().messages().get(
                        userId="me",
                        id=msg_id,
                        format="metadata",
                        metadataHeaders=["From", "Subject", "Date"]
                    ).execute()

                    headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
                    print(f"  Latest: {headers.get('Subject', 'No Subject')[:60]}")
                    print(f"  From: {headers.get('From', 'Unknown')[:60]}")
                    print(f"  Date: {headers.get('Date', 'Unknown')[:40]}")

        except Exception as e:
            print(f"{label}: Error - {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
