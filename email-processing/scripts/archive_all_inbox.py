#!/usr/bin/env python3
"""
Archive all emails from inbox by removing INBOX label.
This achieves inbox zero by moving all emails to All Mail.
"""

import sys
import time
from pathlib import Path

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def archive_all_inbox(service, max_results=None):
    """
    Archive all emails from inbox.

    Args:
        service: Gmail API service object
        max_results: Maximum number of emails to archive (None for all)
    """
    print("📬 Fetching inbox emails...")

    all_message_ids = []
    page_token = None

    while True:
        try:
            results = service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                maxResults=500,
                pageToken=page_token
            ).execute()

            messages = results.get("messages", [])
            if not messages:
                break

            message_ids = [msg["id"] for msg in messages]
            all_message_ids.extend(message_ids)

            print(f"   Collected {len(all_message_ids)} emails...")

            if max_results and len(all_message_ids) >= max_results:
                all_message_ids = all_message_ids[:max_results]
                break

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        except HttpError as e:
            print(f"⚠️  Error fetching emails: {e}")
            break

    if not all_message_ids:
        print("✅ Inbox is already empty!")
        return

    print(f"\n📦 Archiving {len(all_message_ids)} emails...")

    # Process in batches of 1000 (Gmail API limit)
    batch_size = 1000
    archived = 0

    for i in range(0, len(all_message_ids), batch_size):
        batch = all_message_ids[i:i + batch_size]

        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                service.users().messages().batchModify(
                    userId="me",
                    body={
                        "ids": batch,
                        "removeLabelIds": ["INBOX"]
                    }
                ).execute()

                archived += len(batch)
                progress = (archived / len(all_message_ids)) * 100
                print(f"   Progress: {archived}/{len(all_message_ids)} ({progress:.1f}%)")
                break

            except HttpError as e:
                if e.resp.status == 429:  # Rate limit
                    wait_time = 2 ** retry_count  # Exponential backoff
                    print(f"⚠️  Rate limit hit. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    retry_count += 1
                else:
                    print(f"❌ Error archiving batch: {e}")
                    break

        # Small delay between batches
        time.sleep(0.1)

    print(f"\n✅ Archived {archived} emails!")
    print("🎉 INBOX ZERO ACHIEVED! 🎉")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive all emails from inbox"
    )
    parser.add_argument(
        "--refresh-token-secret",
        help="Secret name for Gmail refresh token"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        help="Maximum number of emails to archive"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Auto-confirm without prompting"
    )

    args = parser.parse_args()

    print("🔐 Authenticating with Gmail...")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    print("📧 Building Gmail service...")
    service = build("gmail", "v1", credentials=credentials)

    # Get inbox count
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=1
    ).execute()

    inbox_count = results.get("resultSizeEstimate", 0)

    print(f"✅ Found {inbox_count} emails in inbox")

    if inbox_count == 0:
        print("🎉 Inbox is already at zero!")
        return

    if not args.yes:
        confirm = input(f"\n⚠️  Archive all {inbox_count} emails? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Cancelled")
            return
    else:
        print(f"\n🔄 Archiving {inbox_count} emails (auto-confirmed)...")

    archive_all_inbox(service, max_results=args.max_results)


if __name__ == "__main__":
    main()
