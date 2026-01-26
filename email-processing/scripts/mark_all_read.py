#!/usr/bin/env python3
"""
Mark all unread emails as read (remove UNREAD label).
Quick way to achieve unread zero without processing.
"""

import sys
from pathlib import Path
import time
from googleapiclient.errors import HttpError

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build


def mark_all_as_read(service, batch_size=100):
    """Mark all unread emails as read."""
    try:
        print("📊 Counting unread emails...")

        # Get count first
        results = service.users().messages().list(
            userId="me",
            q="is:unread",
            maxResults=1
        ).execute()

        total_count = results.get("resultSizeEstimate", 0)
        print(f"✅ Found {total_count} unread emails")

        if total_count == 0:
            print("🎉 Already at unread zero!")
            return

        # Ask for confirmation
        print(f"\n⚠️  This will mark ALL {total_count} unread emails as read.")
        print("   This cannot be undone!")
        confirmation = input("\nContinue? [y/N]: ").lower().strip()

        if confirmation != 'y':
            print("❌ Cancelled")
            return

        print(f"\n🔄 Marking {total_count} emails as read...")
        marked_count = 0
        page_token = None

        while True:
            # Get batch of unread messages
            params = {
                "userId": "me",
                "q": "is:unread",
                "maxResults": batch_size
            }
            if page_token:
                params["pageToken"] = page_token

            results = service.users().messages().list(**params).execute()
            messages = results.get("messages", [])

            if not messages:
                break

            # Get message IDs
            message_ids = [msg["id"] for msg in messages]

            # Mark as read in batch
            try:
                service.users().messages().batchModify(
                    userId="me",
                    body={
                        "ids": message_ids,
                        "removeLabelIds": ["UNREAD"]
                    }
                ).execute()

                marked_count += len(message_ids)
                progress_pct = min((marked_count / total_count) * 100, 100)
                print(f"   Progress: {marked_count}/{total_count} ({progress_pct:.1f}%)", end="\r")

                # Small delay to avoid rate limits
                time.sleep(0.5)

            except HttpError as e:
                if e.resp.status == 429:
                    print(f"\n⚠️  Rate limit hit. Waiting 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    raise

            # Check if we have more
            page_token = results.get("nextPageToken")
            if not page_token:
                break

        print(f"\n\n✅ Marked {marked_count} emails as read!")
        print("🎉 UNREAD ZERO ACHIEVED! 🎉")

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Mark all unread emails as read"
    )
    parser.add_argument(
        "--refresh-token-secret",
        help="Secret name for Gmail refresh token"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of emails to process per batch (default: 100)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    print("🔐 Authenticating with Gmail...")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    print("📧 Building Gmail service...")
    service = build("gmail", "v1", credentials=credentials)

    if args.yes:
        # Auto-confirm if --yes flag
        results = service.users().messages().list(
            userId="me",
            q="is:unread",
            maxResults=1
        ).execute()

        total_count = results.get("resultSizeEstimate", 0)
        print(f"✅ Found {total_count} unread emails")

        if total_count == 0:
            print("🎉 Already at unread zero!")
            return

        print(f"\n🔄 Marking {total_count} emails as read (auto-confirmed)...")

        marked_count = 0
        page_token = None

        while True:
            params = {
                "userId": "me",
                "q": "is:unread",
                "maxResults": args.batch_size
            }
            if page_token:
                params["pageToken"] = page_token

            results = service.users().messages().list(**params).execute()
            messages = results.get("messages", [])

            if not messages:
                break

            message_ids = [msg["id"] for msg in messages]

            try:
                service.users().messages().batchModify(
                    userId="me",
                    body={
                        "ids": message_ids,
                        "removeLabelIds": ["UNREAD"]
                    }
                ).execute()

                marked_count += len(message_ids)
                progress_pct = min((marked_count / total_count) * 100, 100)
                print(f"   Progress: {marked_count}/{total_count} ({progress_pct:.1f}%)", end="\r")

                time.sleep(0.5)

            except HttpError as e:
                if e.resp.status == 429:
                    print(f"\n⚠️  Rate limit hit. Waiting 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    raise

            page_token = results.get("nextPageToken")
            if not page_token:
                break

        print(f"\n\n✅ Marked {marked_count} emails as read!")
        print("🎉 UNREAD ZERO ACHIEVED! 🎉")
    else:
        mark_all_as_read(service, args.batch_size)


if __name__ == "__main__":
    main()
