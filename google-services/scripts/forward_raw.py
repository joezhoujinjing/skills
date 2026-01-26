#!/usr/bin/env python3
"""
Forward email with attachments using Gmail API's raw format.
This is the cleanest way - parse and modify the RFC 2822 message.
"""

import sys
import base64
import argparse
from pathlib import Path
from email import message_from_bytes
from email.utils import formataddr, parseaddr

# Add to path
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials, print_auth_info
from googleapiclient.discovery import build


def forward_email_raw(service, message_id, to, body=None):
    """
    Forward email by modifying the raw RFC 2822 message.
    This preserves all attachments without re-encoding.
    """
    try:
        # Get original message in raw format (includes everything)
        orig_message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="raw"
        ).execute()

        # Decode the raw message
        raw_email = base64.urlsafe_b64decode(orig_message['raw'])
        email_msg = message_from_bytes(raw_email)

        # Extract original headers for forward header
        orig_from = email_msg.get('From', '')
        orig_date = email_msg.get('Date', '')
        orig_subject = email_msg.get('Subject', '')
        orig_to = email_msg.get('To', '')

        # Update subject with Fwd: prefix
        subject = orig_subject
        if not subject.lower().startswith('fwd:') and not subject.lower().startswith('fw:'):
            subject = f'Fwd: {subject}'

        # Clear old headers and set new ones
        del email_msg['To']
        del email_msg['From']
        del email_msg['Subject']
        if 'Cc' in email_msg:
            del email_msg['Cc']
        if 'Bcc' in email_msg:
            del email_msg['Bcc']

        # Remove threading headers for new thread
        for header in ['Message-ID', 'In-Reply-To', 'References']:
            if header in email_msg:
                del email_msg[header]

        # Set new headers
        email_msg['To'] = to
        email_msg['Subject'] = subject

        # If body provided, prepend it to the message
        if body:
            # Build forward header
            forward_header = f"""
---------- Forwarded message ---------
From: {orig_from}
Date: {orig_date}
Subject: {orig_subject}
To: {orig_to}

"""
            # Add custom message at the beginning
            if email_msg.is_multipart():
                # For multipart messages, prepend to the first text/plain part
                for part in email_msg.walk():
                    if part.get_content_type() == 'text/plain' and not part.is_multipart():
                        orig_payload = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        new_payload = f"{body}\n{forward_header}{orig_payload}"
                        part.set_payload(new_payload, charset='utf-8')
                        break
            else:
                # For simple messages, prepend to payload
                orig_payload = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                new_payload = f"{body}\n{forward_header}{orig_payload}"
                email_msg.set_payload(new_payload, charset='utf-8')

        # Encode and send
        raw = base64.urlsafe_b64encode(email_msg.as_bytes()).decode()
        send_body = {'raw': raw}

        result = service.users().messages().send(userId='me', body=send_body).execute()

        print(f"✅ Forward sent successfully (using raw format)!")
        print(f"   Message ID: {result['id']}")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")
        print(f"   Method: RFC 2822 raw format (preserves all attachments)")

    except Exception as e:
        print(f"❌ Error forwarding message: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Forward email with attachments using raw format"
    )
    parser.add_argument("--message-id", required=True, help="Gmail message ID to forward")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--body", help="Optional message body to prepend")

    args = parser.parse_args()

    print_auth_info("Gmail")
    credentials = get_credentials()
    service = build("gmail", "v1", credentials=credentials)

    forward_email_raw(service, args.message_id, args.to, args.body)


if __name__ == "__main__":
    main()
