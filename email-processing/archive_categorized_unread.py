#!/usr/bin/env python3
"""
Archive all unread emails in category tabs (Updates, Promotions, Social, Forums).
These are technically in inbox but categorized.
"""

import argparse
import sys
from pathlib import Path
import time
from googleapiclient.errors import HttpError

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials
from googleapiclient.discovery import build


def fetch_with_retry(func, max_retries=5, initial_delay=1):
    """Retry API calls with exponential backoff for rate limit errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit error
                delay = initial_delay * (2 ** attempt)
                print(f"\n⚠️  Rate limit hit. Waiting {delay}s before retry (attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
                if attempt == max_retries - 1:
                    raise
            else:
                print(f"\n❌ HTTP Error {e.resp.status}: {e.reason}", file=sys.stderr)
                raise
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
            raise
    return None


def get_categorized_unread(service):
    """Get all unread messages in category tabs."""
    try:
        all_messages = []

        # Query for each category separately
        categories = [
            ("CATEGORY_UPDATES", "Updates"),
            ("CATEGORY_PROMOTIONS", "Promotions"),
            ("CATEGORY_SOCIAL", "Social"),
            ("CATEGORY_FORUMS", "Forums"),
        ]

        for category_label, category_name in categories:
            print(f"\n📊 Fetching unread {category_name}...")
            page_token = None
            category_messages = []

            while True:
                params = {
                    "userId": "me",
                    "maxResults": 500,
                    "labelIds": ["UNREAD", category_label]
                }
                if page_token:
                    params["pageToken"] = page_token

                results = fetch_with_retry(
                    lambda: service.users().messages().list(**params).execute()
                )
                messages = results.get("messages", [])
                category_messages.extend(messages)

                print(f"   Found {len(category_messages)} unread {category_name}...", end="\r")

                page_token = results.get("nextPageToken")
                if not page_token:
                    break

            print(f"   ✅ {len(category_messages):,} unread in {category_name}    ")
            all_messages.extend(category_messages)

        print(f"\n✅ Total: {len(all_messages):,} unread categorized messages")
        return all_messages

    except Exception as e:
        print(f"❌ Error fetching messages: {e}", file=sys.stderr)
        return []


def archive_messages_batch(service, message_ids, batch_size=1000):
    """Archive and mark as read by removing INBOX and UNREAD labels."""
    try:
        total = len(message_ids)
        archived = 0
        errors = 0

        print(f"\n📦 Archiving {total:,} messages in batches of {batch_size}...")

        for i in range(0, total, batch_size):
            batch = message_ids[i:i + batch_size]

            try:
                # Progress
                progress_pct = (i / total) * 100
                bar_width = 40
                filled = int(bar_width * i / total) if total > 0 else 0
                bar = "█" * filled + "░" * (bar_width - filled)
                print(f"   [{bar}] {i}/{total} ({progress_pct:.1f}%)    ", end="\r")

                # Archive by removing INBOX and UNREAD labels
                body = {
                    "ids": batch,
                    "removeLabelIds": ["INBOX", "UNREAD"]
                }

                fetch_with_retry(
                    lambda: service.users().messages().batchModify(
                        userId="me",
                        body=body
                    ).execute()
                )

                archived += len(batch)

                # Small delay to avoid rate limits
                time.sleep(0.1)

            except Exception as e:
                print(f"\n⚠️  Error archiving batch: {e}")
                errors += len(batch)
                continue

        # Final progress
        print(f"   [{'█' * bar_width}] {total}/{total} (100.0%)    ")

        print(f"\n✅ Successfully archived {archived:,} messages")
        if errors > 0:
            print(f"⚠️  Failed to archive {errors:,} messages")

        return archived

    except Exception as e:
        print(f"❌ Fatal error during archiving: {e}", file=sys.stderr)
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Archive all unread emails in category tabs (Updates, Promotions, Social, Forums)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be archived without actually archiving"
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

    # Get messages
    messages = get_categorized_unread(service)

    if not messages:
        print("\n✨ No unread categorized messages found. Nothing to archive!")
        return

    message_ids = [msg["id"] for msg in messages]

    if args.dry_run:
        print(f"\n🔍 DRY RUN: Would archive {len(message_ids):,} messages")
        print("   Run without --dry-run flag to actually archive them")
        return

    # Confirm with user
    print(f"\n⚠️  This will archive {len(message_ids):,} unread messages from:")
    print("   • Updates, Promotions, Social, Forums tabs")
    print("   • Messages will be removed from inbox/categories")
    print("   • Messages will be marked as READ and archived to 'All Mail'")

    response = input("\n   Continue? (yes/no): ").strip().lower()

    if response not in ["yes", "y"]:
        print("❌ Cancelled. No messages were archived.")
        return

    # Archive messages
    archived = archive_messages_batch(service, message_ids)

    print(f"\n🎉 Done! Archived {archived:,} messages.")
    print(f"   Your inbox should now only show primary inbox messages.")


if __name__ == "__main__":
    main()
