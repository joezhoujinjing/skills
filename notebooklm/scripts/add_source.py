#!/usr/bin/env python3
"""Add a source to a NotebookLM notebook."""

import argparse
import json
import sys
from pathlib import Path
from _client import get_client


def main():
    parser = argparse.ArgumentParser(description="Add a source to a NotebookLM notebook")
    parser.add_argument("notebook_id", help="Notebook ID")
    parser.add_argument("--url", help="URL to add (website or YouTube)")
    parser.add_argument("--text", help="Text content to add")
    parser.add_argument("--file", help="Local file to upload")
    parser.add_argument("--title", help="Title for the source (for text/file sources)")
    parser.add_argument("--wait", action="store_true", help="Wait for source to finish processing")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Validate inputs
    source_types = sum([bool(args.url), bool(args.text), bool(args.file)])
    if source_types == 0:
        print("Error: Must specify --url, --text, or --file", file=sys.stderr)
        sys.exit(1)
    if source_types > 1:
        print("Error: Can only specify one of --url, --text, or --file", file=sys.stderr)
        sys.exit(1)

    client = get_client()

    try:
        source_id = None
        source_type = None

        if args.url:
            source_type = "url"
            title = args.title or args.url
            result = client.add_url_source(args.notebook_id, args.url, title)
            if result and isinstance(result, dict):
                source_id = result.get("id") or result.get("source_id")

        elif args.text:
            source_type = "text"
            title = args.title or "Text Source"
            result = client.add_text_source(args.notebook_id, args.text, title)
            if result and isinstance(result, dict):
                source_id = result.get("id") or result.get("source_id")

        elif args.file:
            source_type = "file"
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File not found: {args.file}", file=sys.stderr)
                sys.exit(1)

            result = client.upload_file(args.notebook_id, str(file_path))
            if result and isinstance(result, dict):
                source_id = result.get("id") or result.get("source_id")

        if not source_id:
            print("Error: Failed to add source", file=sys.stderr)
            sys.exit(1)

        # Wait for source to be ready if requested
        if args.wait:
            if not args.json:
                print(f"Waiting for source {source_id} to be ready...", file=sys.stderr)
            try:
                client.wait_for_source_ready(args.notebook_id, source_id, timeout=180.0)
                if not args.json:
                    print("Source is ready!", file=sys.stderr)
            except TimeoutError:
                print("Warning: Source not ready after 180s", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Error waiting for source: {e}", file=sys.stderr)

        if args.json:
            print(json.dumps({
                "notebook_id": args.notebook_id,
                "source_id": source_id,
                "source_type": source_type,
                "title": args.title,
            }, indent=2))
        else:
            print(f"Added {source_type} source: {source_id}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
