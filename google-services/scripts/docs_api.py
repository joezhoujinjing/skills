#!/usr/bin/env python3
"""
Google Docs API helper for Google Services skill.
"""

import argparse
import sys
from googleapiclient.discovery import build
from oauth_helper import get_credentials, print_auth_info


def create_document(service, title, content=None):
    """Create a new Google Doc."""
    try:
        document = {"title": title}
        doc = service.documents().create(body=document).execute()

        doc_id = doc["documentId"]
        print(f"✅ Document created successfully!")
        print(f"   Title: {doc['title']}")
        print(f"   ID: {doc_id}")
        print(f"   Link: https://docs.google.com/document/d/{doc_id}/edit")

        # Add initial content if provided
        if content:
            requests = [{
                "insertText": {
                    "location": {"index": 1},
                    "text": content
                }
            }]
            service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
            print(f"   Added initial content ({len(content)} characters)")

        return doc_id

    except Exception as e:
        print(f"❌ Error creating document: {e}", file=sys.stderr)
        sys.exit(1)


def read_document(service, document_id):
    """Read a Google Doc."""
    try:
        doc = service.documents().get(documentId=document_id).execute()

        title = doc.get("title")
        content = extract_text(doc.get("body").get("content"))

        print(f"\n{'=' * 100}")
        print(f"Document: {title}")
        print(f"ID: {document_id}")
        print(f"Link: https://docs.google.com/document/d/{document_id}/edit")
        print(f"{'=' * 100}\n")
        print(content)
        print(f"\n{'=' * 100}")

    except Exception as e:
        print(f"❌ Error reading document: {e}", file=sys.stderr)
        sys.exit(1)


def extract_text(content):
    """Extract text from document content."""
    text = ""
    for element in content:
        if "paragraph" in element:
            for el in element["paragraph"]["elements"]:
                if "textRun" in el:
                    text += el["textRun"]["content"]
    return text


def append_text(service, document_id, text):
    """Append text to a Google Doc."""
    try:
        # Get current document to find end index
        doc = service.documents().get(documentId=document_id).execute()
        end_index = doc["body"]["content"][-1]["endIndex"] - 1

        requests = [{
            "insertText": {
                "location": {"index": end_index},
                "text": text
            }
        }]

        service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()

        print(f"✅ Text appended successfully!")
        print(f"   Added {len(text)} characters")
        print(f"   Link: https://docs.google.com/document/d/{document_id}/edit")

    except Exception as e:
        print(f"❌ Error appending text: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Google Docs API Helper")
    parser.add_argument("command", choices=["create", "read", "append"],
                        help="Command to execute")
    parser.add_argument("--title", help="Document title")
    parser.add_argument("--content", help="Document content")
    parser.add_argument("--document-id", help="Document ID")
    parser.add_argument("--text", help="Text to append")
    parser.add_argument("--refresh-token-secret", help="Secret name for refresh token")

    args = parser.parse_args()

    # Get credentials
    print_auth_info("Docs")
    credentials = get_credentials(refresh_token_secret=args.refresh_token_secret)

    # Build Docs service
    service = build("docs", "v1", credentials=credentials)

    # Execute command
    if args.command == "create":
        if not args.title:
            print("❌ --title is required for create command", file=sys.stderr)
            sys.exit(1)
        create_document(service, args.title, content=args.content)
    elif args.command == "read":
        if not args.document_id:
            print("❌ --document-id is required for read command", file=sys.stderr)
            sys.exit(1)
        read_document(service, args.document_id)
    elif args.command == "append":
        if not args.document_id or not args.text:
            print("❌ --document-id and --text are required for append command", file=sys.stderr)
            sys.exit(1)
        append_text(service, args.document_id, args.text)


if __name__ == "__main__":
    main()
