#!/usr/bin/env python3
"""
Send a reply to an email.
"""

import sys
import base64
from pathlib import Path
from email.mime.text import MIMEText
from googleapiclient.discovery import build

# Import from google-services skill
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials


def send_reply(service, thread_id, to, subject, body):
    """Send a reply email."""
    try:
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Send with threadId to keep in conversation
        send_message = {
            'raw': raw_message,
            'threadId': thread_id
        }

        result = service.users().messages().send(
            userId='me',
            body=send_message
        ).execute()

        print(f"✅ Reply sent successfully!")
        print(f"   Message ID: {result['id']}")
        return result

    except Exception as e:
        print(f"❌ Error sending reply: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 5:
        print("Usage: python send_reply.py <thread_id> <to> <subject> <body>")
        sys.exit(1)

    thread_id = sys.argv[1]
    to = sys.argv[2]
    subject = sys.argv[3]
    body = sys.argv[4]

    print("🔐 Authenticating with Gmail...")
    credentials = get_credentials()

    print("📧 Building Gmail service...")
    service = build("gmail", "v1", credentials=credentials)

    print(f"📤 Sending reply to {to}...")
    send_reply(service, thread_id, to, subject, body)


if __name__ == "__main__":
    main()
