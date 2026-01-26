#!/usr/bin/env python3
"""
Gmail API helper for Google Services skill.
"""

import argparse
import base64
import sys
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from oauth_helper import get_credentials, print_auth_info


def list_messages(service, max_results=10, query=None):
    """List Gmail messages."""
    try:
        params = {"userId": "me", "maxResults": max_results}
        if query:
            params["q"] = query

        results = service.users().messages().list(**params).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return

        print(f"Found {len(messages)} messages:\n")
        print("=" * 100)

        for msg in messages:
            message = service.users().messages().get(userId="me", id=msg["id"], format="metadata").execute()
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}

            from_addr = headers.get("From", "Unknown")
            subject = headers.get("Subject", "No Subject")
            date = headers.get("Date", "Unknown")
            snippet = message.get("snippet", "")

            print(f"\n📧 ID: {msg['id']}")
            print(f"From: {from_addr}")
            print(f"Subject: {subject}")
            print(f"Date: {date}")
            print(f"Preview: {snippet}")
            print("=" * 100)

    except Exception as e:
        print(f"❌ Error listing messages: {e}", file=sys.stderr)
        sys.exit(1)


def read_message(service, message_id):
    """Read a specific Gmail message."""
    try:
        message = service.users().messages().get(userId="me", id=message_id, format="full").execute()

        headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
        print("\n" + "=" * 100)
        print(f"Message ID: {message_id}")
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"To: {headers.get('To', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', 'No Subject')}")
        print(f"Date: {headers.get('Date', 'Unknown')}")
        print("=" * 100)

        # Extract body
        body = extract_body(message["payload"])
        if body:
            print(f"\n{body}")
        else:
            print("\n(No text content)")

        print("\n" + "=" * 100)

    except Exception as e:
        print(f"❌ Error reading message: {e}", file=sys.stderr)
        sys.exit(1)


def extract_body(payload):
    """Extract email body from payload."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                if "data" in part["body"]:
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
            elif "parts" in part:
                result = extract_body(part)
                if result:
                    return result
    elif "body" in payload and "data" in payload["body"]:
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
    return None


def search_messages(service, query, max_results=20):
    """Search Gmail messages."""
    list_messages(service, max_results=max_results, query=query)


def send_message(service, to, subject, body, cc=None, bcc=None):
    """Send an email."""
    try:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {"raw": raw}

        result = service.users().messages().send(userId="me", body=send_message).execute()
        print(f"✅ Message sent successfully!")
        print(f"   Message ID: {result['id']}")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")

    except Exception as e:
        print(f"❌ Error sending message: {e}", file=sys.stderr)
        sys.exit(1)


def get_message_for_reply(service, message_id):
    """Get message details needed for reply/forward."""
    message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
    body = extract_body(message["payload"]) or ""
    return {
        "id": message_id,
        "threadId": message["threadId"],
        "from": headers.get("From", ""),
        "to": headers.get("To", ""),
        "cc": headers.get("Cc", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "message_id": headers.get("Message-ID", ""),
        "references": headers.get("References", ""),
        "body": body,
    }


def parse_email_address(addr_string):
    """Extract email address from 'Name <email>' format."""
    import re
    match = re.search(r'<([^>]+)>', addr_string)
    if match:
        return match.group(1)
    return addr_string.strip()


def reply_message(service, message_id, body, reply_all=False, to_override=None):
    """Reply to an email. Optionally reply-all or specify recipients."""
    try:
        orig = get_message_for_reply(service, message_id)

        # Determine recipients
        if to_override:
            to = to_override
            cc = None
        elif reply_all:
            # Reply to sender + all original To/CC (excluding self)
            to = orig["from"]
            # Combine original To and CC, filter later if needed
            cc_list = []
            if orig["to"]:
                cc_list.extend([addr.strip() for addr in orig["to"].split(",")])
            if orig["cc"]:
                cc_list.extend([addr.strip() for addr in orig["cc"].split(",")])
            cc = ", ".join(cc_list) if cc_list else None
        else:
            # Simple reply to sender
            to = orig["from"]
            cc = None

        # Build subject with Re: prefix
        subject = orig["subject"]
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        # Build reply body with quoted original
        quoted_body = "\n".join(f"> {line}" for line in orig["body"].split("\n"))
        full_body = f"{body}\n\nOn {orig['date']}, {orig['from']} wrote:\n{quoted_body}"

        # Create message
        message = MIMEText(full_body)
        message["to"] = to
        message["subject"] = subject
        if cc:
            message["cc"] = cc

        # Set reply headers
        if orig["message_id"]:
            message["In-Reply-To"] = orig["message_id"]
            refs = orig["references"]
            message["References"] = f"{refs} {orig['message_id']}".strip() if refs else orig["message_id"]

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_body = {"raw": raw, "threadId": orig["threadId"]}

        result = service.users().messages().send(userId="me", body=send_body).execute()
        mode = "Reply-All" if reply_all else ("Reply to specific" if to_override else "Reply")
        print(f"✅ {mode} sent successfully!")
        print(f"   Message ID: {result['id']}")
        print(f"   Thread ID: {result['threadId']}")
        print(f"   To: {to}")
        if cc:
            print(f"   CC: {cc}")
        print(f"   Subject: {subject}")

    except Exception as e:
        print(f"❌ Error sending reply: {e}", file=sys.stderr)
        sys.exit(1)


def get_attachments(service, message_id, message_payload):
    """Extract all attachments from a message."""
    attachments = []

    def process_parts(parts):
        for part in parts:
            if part.get('filename'):
                attachment_id = part['body'].get('attachmentId')
                if attachment_id:
                    # Download attachment
                    att = service.users().messages().attachments().get(
                        userId='me',
                        messageId=message_id,
                        id=attachment_id
                    ).execute()

                    data = base64.urlsafe_b64decode(att['data'])
                    attachments.append({
                        'filename': part['filename'],
                        'mimeType': part['mimeType'],
                        'data': data
                    })

            if 'parts' in part:
                process_parts(part['parts'])

    if 'parts' in message_payload:
        process_parts(message_payload['parts'])

    return attachments


def forward_message(service, message_id, to, body=None):
    """Forward an email to new recipients with attachments preserved."""
    try:
        # Get original message with full payload
        orig_message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in orig_message["payload"]["headers"]}
        orig_body = extract_body(orig_message["payload"]) or ""

        # Build subject with Fwd: prefix
        subject = headers.get("Subject", "")
        if not subject.lower().startswith("fwd:") and not subject.lower().startswith("fw:"):
            subject = f"Fwd: {subject}"

        # Get attachments
        attachments = get_attachments(service, message_id, orig_message["payload"])

        # Create multipart message
        message = MIMEMultipart()
        message["to"] = to
        message["subject"] = subject

        # Build forward body
        forward_header = f"""
---------- Forwarded message ---------
From: {headers.get('From', '')}
Date: {headers.get('Date', '')}
Subject: {headers.get('Subject', '')}
To: {headers.get('To', '')}
"""
        if body:
            full_body = f"{body}\n{forward_header}\n{orig_body}"
        else:
            full_body = f"{forward_header}\n{orig_body}"

        # Attach text body
        message.attach(MIMEText(full_body, 'plain'))

        # Attach files
        for att in attachments:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(att['data'])
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{att["filename"]}"')
            message.attach(part)

        # Send
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_body = {"raw": raw}

        result = service.users().messages().send(userId="me", body=send_body).execute()
        print(f"✅ Forward sent successfully!")
        print(f"   Message ID: {result['id']}")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")
        if attachments:
            print(f"   Attachments: {len(attachments)} file(s)")
            for att in attachments:
                print(f"     • {att['filename']}")

    except Exception as e:
        print(f"❌ Error forwarding message: {e}", file=sys.stderr)
        sys.exit(1)


def get_labels(service):
    """List Gmail labels."""
    try:
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])

        if not labels:
            print("No labels found.")
            return

        print(f"Found {len(labels)} labels:\n")
        for label in labels:
            print(f"  • {label['name']} (ID: {label['id']})")

    except Exception as e:
        print(f"❌ Error listing labels: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gmail API Helper")
    parser.add_argument("command", choices=["list", "read", "search", "send", "reply", "forward", "labels"],
                        help="Command to execute")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results to return")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--message-id", help="Message ID for read/reply/forward commands")
    parser.add_argument("--to", help="Recipient email address")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Email body")
    parser.add_argument("--cc", help="CC recipients")
    parser.add_argument("--bcc", help="BCC recipients")
    parser.add_argument("--reply-all", action="store_true", help="Reply to all recipients")
    parser.add_argument("--refresh-token-secret", help="Secret name for refresh token")

    args = parser.parse_args()

    # Get credentials
    print_auth_info("Gmail")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    # Build Gmail service
    service = build("gmail", "v1", credentials=credentials)

    # Execute command
    if args.command == "list":
        list_messages(service, max_results=args.max_results, query=args.query)
    elif args.command == "read":
        if not args.message_id:
            print("❌ --message-id is required for read command", file=sys.stderr)
            sys.exit(1)
        read_message(service, args.message_id)
    elif args.command == "search":
        if not args.query:
            print("❌ --query is required for search command", file=sys.stderr)
            sys.exit(1)
        search_messages(service, args.query, max_results=args.max_results)
    elif args.command == "send":
        if not all([args.to, args.subject, args.body]):
            print("❌ --to, --subject, and --body are required for send command", file=sys.stderr)
            sys.exit(1)
        send_message(service, args.to, args.subject, args.body, cc=args.cc, bcc=args.bcc)
    elif args.command == "reply":
        if not args.message_id:
            print("❌ --message-id is required for reply command", file=sys.stderr)
            sys.exit(1)
        if not args.body:
            print("❌ --body is required for reply command", file=sys.stderr)
            sys.exit(1)
        reply_message(service, args.message_id, args.body, reply_all=args.reply_all, to_override=args.to)
    elif args.command == "forward":
        if not args.message_id:
            print("❌ --message-id is required for forward command", file=sys.stderr)
            sys.exit(1)
        if not args.to:
            print("❌ --to is required for forward command", file=sys.stderr)
            sys.exit(1)
        forward_message(service, args.message_id, args.to, body=args.body)
    elif args.command == "labels":
        get_labels(service)


if __name__ == "__main__":
    main()
