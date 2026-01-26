#!/usr/bin/env python3
"""
Export ALL unread Gmail messages (from anywhere, not just inbox) to YAML format.
"""

import argparse
import sys
import yaml
from pathlib import Path
import datetime
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


def get_all_unread_emails(service, max_results=None):
    """Get ALL unread emails (from anywhere) using pagination."""
    try:
        # Query for all unread messages
        all_messages = []
        page_token = None

        print("📊 Fetching ALL unread messages (from anywhere in Gmail)...")

        # Paginate through all messages
        while True:
            params = {
                "userId": "me",
                "maxResults": 500,  # Max per page
                "q": "is:unread"  # All unread messages
            }
            if page_token:
                params["pageToken"] = page_token

            results = fetch_with_retry(
                lambda: service.users().messages().list(**params).execute()
            )
            messages = results.get("messages", [])
            all_messages.extend(messages)

            print(f"   Retrieved {len(all_messages)} messages so far...", end="\r")

            page_token = results.get("nextPageToken")
            if not page_token:
                break

            # Check if we've hit the limit
            if max_results and len(all_messages) >= max_results:
                all_messages = all_messages[:max_results]
                break

        print(f"\n✅ Found {len(all_messages)} total unread messages")

        if not all_messages:
            print("No unread messages found.")
            return []

        print(f"📥 Fetching detailed metadata for all messages...")
        print(f"   Progress: 0/{len(all_messages)} (0.0%)")

        email_data = []
        errors = []

        for i, msg in enumerate(all_messages, 1):
            try:
                # Progress bar
                progress_pct = (i / len(all_messages)) * 100
                bar_width = 40
                filled = int(bar_width * i / len(all_messages))
                bar = "█" * filled + "░" * (bar_width - filled)

                print(f"   [{bar}] {i}/{len(all_messages)} ({progress_pct:.1f}%)    ", end="\r")

                # Get full message details with retry
                message = fetch_with_retry(
                    lambda: service.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="metadata",
                        metadataHeaders=["From", "To", "Cc", "Subject", "Date"]
                    ).execute()
                )

                # Extract headers
                headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}

                # Build email data structure
                email_info = {
                    "message_id": msg["id"],
                    "thread_id": message.get("threadId"),
                    "snippet": message.get("snippet", ""),
                    "labels": message.get("labelIds", []),
                    "metadata": {
                        "from": headers.get("From", ""),
                        "to": headers.get("To", ""),
                        "cc": headers.get("Cc", ""),
                        "subject": headers.get("Subject", "No Subject"),
                        "date": headers.get("Date", ""),
                    },
                    "internal_date": message.get("internalDate"),
                    "size_estimate": message.get("sizeEstimate"),
                }

                email_data.append(email_info)

            except Exception as e:
                error_msg = f"Failed to fetch message {msg['id']}: {e}"
                errors.append(error_msg)
                print(f"\n⚠️  {error_msg}")
                # Continue processing other messages

        print()  # New line after progress

        if errors:
            print(f"\n⚠️  {len(errors)} messages failed to fetch:")
            for err in errors[:5]:  # Show first 5 errors
                print(f"   - {err}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")

        print(f"✅ Successfully fetched {len(email_data)} out of {len(all_messages)} messages")
        return email_data

    except Exception as e:
        print(f"\n❌ Fatal error fetching messages: {e}", file=sys.stderr)
        sys.exit(1)


def save_to_yaml(email_data, output_dir):
    """Save email data to YAML file."""
    try:
        # Always save to skill directory
        skill_dir = Path(__file__).parent.parent
        skill_output = skill_dir / "data" / "emails_dump.yaml"

        with open(skill_output, "w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "export_date": datetime.datetime.now().isoformat(),
                    "total_emails": len(email_data),
                    "emails": email_data
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )

        print(f"✅ Saved to skill directory: {skill_output}")

        # Also save timestamped backup
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = output_dir / f"unread_emails_{timestamp}.yaml"

        with open(backup_file, "w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "export_date": datetime.datetime.now().isoformat(),
                    "total_emails": len(email_data),
                    "emails": email_data
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )

        print(f"✅ Backup saved to: {backup_file}")

        return skill_output

    except Exception as e:
        print(f"❌ Error saving to YAML: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Export ALL unread Gmail messages (from anywhere) to YAML"
    )
    parser.add_argument(
        "--output-dir",
        default="~/email_triage",
        help="Output directory for YAML file (default: ~/email_triage)"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=None,
        help="Maximum number of emails to fetch (default: all emails)"
    )
    parser.add_argument(
        "--refresh-token-secret",
        help="Secret name for Gmail refresh token"
    )

    args = parser.parse_args()

    # Expand home directory
    output_dir = Path(args.output_dir).expanduser()

    print("🔐 Authenticating with Gmail...")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    print("📧 Building Gmail service...")
    service = build("gmail", "v1", credentials=credentials)

    print("📥 Fetching ALL unread emails...")
    email_data = get_all_unread_emails(service, max_results=args.max_results)

    if email_data:
        print("💾 Saving to YAML file...")
        save_to_yaml(email_data, output_dir)
    else:
        print("✨ No unread emails!")


if __name__ == "__main__":
    main()
