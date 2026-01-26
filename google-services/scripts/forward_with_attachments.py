#!/usr/bin/env python3
"""
Forward email with attachments preserved.
"""

import sys
import base64
import argparse
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Add to path
sys.path.insert(0, str(Path.home() / ".claude/skills/google-services/scripts"))
from oauth_helper import get_credentials, print_auth_info
from googleapiclient.discovery import build


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


def forward_with_attachments(service, message_id, to, body=None):
    """Forward an email with attachments preserved."""
    try:
        # Get original message
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
        print(f"✅ Forward sent successfully with {len(attachments)} attachment(s)!")
        print(f"   Message ID: {result['id']}")
        print(f"   To: {to}")
        print(f"   Subject: {subject}")
        if attachments:
            print(f"\n   Attachments:")
            for att in attachments:
                print(f"     • {att['filename']}")

    except Exception as e:
        print(f"❌ Error forwarding message: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Forward email with attachments")
    parser.add_argument("--message-id", required=True, help="Gmail message ID to forward")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--body", help="Optional message body to prepend")

    args = parser.parse_args()

    print_auth_info("Gmail")
    credentials = get_credentials()
    service = build("gmail", "v1", credentials=credentials)

    forward_with_attachments(service, args.message_id, args.to, args.body)


if __name__ == "__main__":
    main()
