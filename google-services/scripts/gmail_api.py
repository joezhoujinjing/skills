#!/usr/bin/env python3
"""
Gmail API helper for Google Services skill.
"""

import argparse
import base64
import sys
import json
from email.mime.text import MIMEText
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
    parser.add_argument("command", choices=["list", "read", "search", "send", "labels"],
                        help="Command to execute")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results to return")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--message-id", help="Message ID for read command")
    parser.add_argument("--to", help="Recipient email address")
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--body", help="Email body")
    parser.add_argument("--cc", help="CC recipients")
    parser.add_argument("--bcc", help="BCC recipients")
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
    elif args.command == "labels":
        get_labels(service)


if __name__ == "__main__":
    main()
