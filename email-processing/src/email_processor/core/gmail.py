"""Gmail API client."""

import sys
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from email.utils import parsedate_to_datetime

# Add google-services skill to path
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))

try:
    from oauth_helper import get_credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("⚠️  Warning: google-services skill not found. Gmail features will not work.")
    get_credentials = None
    build = None
    HttpError = Exception

from ..models.email import Email


class GmailClient:
    """Gmail API client with batch operations."""

    def __init__(self, account_config: dict):
        self.account_config = account_config
        self.email = account_config['email']
        self.gmail_refresh_token = account_config['gmail_refresh_token']
        self.service = None

    def _init_service(self):
        """Initialize Gmail service (lazy)."""
        if self.service is None:
            value = self.gmail_refresh_token
            if value.startswith("gsm:"):
                # Pass secret name to oauth_helper (it fetches from GSM internally)
                credentials = get_credentials(refresh_token_secret=value[4:])
            else:
                # Raw refresh token — use oauth_helper with the token value directly
                credentials = get_credentials(refresh_token_secret=value)
            self.service = build("gmail", "v1", credentials=credentials)

    async def fetch_inbox(self, max_results: Optional[int] = None) -> List[Email]:
        """Fetch all inbox emails."""
        self._init_service()

        try:
            # Fetch message IDs
            all_messages = []
            page_token = None

            print("   Fetching message IDs...")

            while True:
                params = {
                    "userId": "me",
                    "maxResults": 500,
                    "q": "in:inbox OR is:unread"
                }
                if page_token:
                    params["pageToken"] = page_token

                results = self.service.users().messages().list(**params).execute()
                messages = results.get("messages", [])
                all_messages.extend(messages)

                print(f"   Retrieved {len(all_messages)} message IDs...", end="\r")

                page_token = results.get("nextPageToken")
                if not page_token:
                    break

                if max_results and len(all_messages) >= max_results:
                    all_messages = all_messages[:max_results]
                    break

            print(f"\n   ✅ Found {len(all_messages)} total messages")

            if not all_messages:
                return []

            # Fetch details in batches with retry + exponential backoff
            import time
            print(f"   Fetching email details (batch)...")
            emails = []
            results_map = {}

            batch_size = 50
            max_retries = 4
            pending_msgs = list(all_messages)
            total = len(pending_msgs)
            batch_num = 0

            while pending_msgs:
                batch_num += 1
                chunk = pending_msgs[:batch_size]
                pending_msgs = pending_msgs[batch_size:]

                failed_ids = []

                def make_callback(msg_id, failed_list):
                    def callback(_request_id, response, exception):
                        if exception:
                            failed_list.append(msg_id)
                        else:
                            results_map[msg_id] = response
                    return callback

                batch = self.service.new_batch_http_request()
                for msg in chunk:
                    batch.add(
                        self.service.users().messages().get(
                            userId="me",
                            id=msg["id"],
                            format="metadata",
                            metadataHeaders=["From", "To", "Cc", "Subject", "Date"]
                        ),
                        callback=make_callback(msg["id"], failed_ids)
                    )
                batch.execute()

                succeeded = len(chunk) - len(failed_ids)
                fetched_so_far = len(results_map)
                print(f"   ✅ Batch {batch_num}: {succeeded}/{len(chunk)} ok ({fetched_so_far}/{total} total)")

                # Retry failed IDs with exponential backoff
                if failed_ids:
                    retry_ids = failed_ids
                    for attempt in range(1, max_retries + 1):
                        delay = 2 ** attempt  # 2, 4, 8, 16 seconds
                        print(f"   🔄 Retry {attempt}/{max_retries}: {len(retry_ids)} emails (waiting {delay}s)...")
                        time.sleep(delay)

                        still_failed = []
                        retry_batch = self.service.new_batch_http_request()
                        for msg_id in retry_ids:
                            retry_batch.add(
                                self.service.users().messages().get(
                                    userId="me",
                                    id=msg_id,
                                    format="metadata",
                                    metadataHeaders=["From", "To", "Cc", "Subject", "Date"]
                                ),
                                callback=make_callback(msg_id, still_failed)
                            )
                        retry_batch.execute()

                        recovered = len(retry_ids) - len(still_failed)
                        if recovered:
                            print(f"      ✅ Recovered {recovered} emails")
                        retry_ids = still_failed
                        if not retry_ids:
                            break

                    if retry_ids:
                        print(f"   ⚠️  {len(retry_ids)} emails failed after {max_retries} retries")

                # Delay between batches to avoid hitting rate limits
                if pending_msgs:
                    time.sleep(1)

            # Build Email objects in original order
            for msg in all_messages:
                message = results_map.get(msg["id"])
                if not message:
                    continue

                headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}

                date_str = headers.get("Date", "")
                try:
                    date = parsedate_to_datetime(date_str)
                except:
                    date = datetime.now()

                email = Email(
                    message_id=msg["id"],
                    thread_id=message.get("threadId"),
                    account=self.account_config.get('account_type', 'unknown'),
                    from_addr=headers.get("From", ""),
                    to_addr=headers.get("To", ""),
                    cc_addr=headers.get("Cc"),
                    subject=headers.get("Subject", "No Subject"),
                    date=date,
                    snippet=message.get("snippet", ""),
                    labels=message.get("labelIds", [])
                )
                emails.append(email)

            return emails

        except HttpError as e:
            print(f"\n❌ Gmail API error: {e}")
            return []

    async def archive_batch(self, message_ids: List[str], batch_size: int = 100):
        """Archive multiple emails in batches."""
        self._init_service()

        if not message_ids:
            return

        total = len(message_ids)
        archived = 0

        for i in range(0, total, batch_size):
            chunk = message_ids[i:i + batch_size]

            try:
                body = {
                    "ids": chunk,
                    "removeLabelIds": ["INBOX", "UNREAD"]
                }

                self.service.users().messages().batchModify(
                    userId="me",
                    body=body
                ).execute()

                archived += len(chunk)
                print(f"   ✅ Archived batch {i//batch_size + 1} ({len(chunk)} emails) - Total: {archived}/{total}")

                # Brief delay to be nice to API
                await asyncio.sleep(0.5)

            except HttpError as e:
                print(f"   ❌ Failed to archive batch: {e}")

    async def archive(self, message_id: str):
        """Archive a single email."""
        await self.archive_batch([message_id])

    async def count_inbox(self) -> int:
        """Count emails in inbox."""
        self._init_service()

        try:
            results = self.service.users().messages().list(
                userId="me",
                q="in:inbox",
                maxResults=1
            ).execute()

            return results.get("resultSizeEstimate", 0)

        except HttpError as e:
            print(f"❌ Error counting inbox: {e}")
            return 0

    def get_email_body(self, message_id: str) -> str:
        """Fetch full email body."""
        self._init_service()

        try:
            message = self.service.users().messages().get(
                userId="me",
                id=message_id,
                format="full"
            ).execute()

            # Extract body (simplified - handle multipart in production)
            payload = message.get("payload", {})
            body_data = payload.get("body", {}).get("data", "")

            if body_data:
                import base64
                return base64.urlsafe_b64decode(body_data).decode('utf-8')

            # Try parts
            parts = payload.get("parts", [])
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        import base64
                        return base64.urlsafe_b64decode(data).decode('utf-8')

            return "[No body content]"

        except Exception as e:
            return f"[Error fetching body: {e}]"
