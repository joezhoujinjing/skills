#!/usr/bin/env python3
"""List all NotebookLM notebooks."""

import argparse
import json
import sys
from _client import get_client


def main():
    parser = argparse.ArgumentParser(description="List all NotebookLM notebooks")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    client = get_client()

    try:
        notebooks = client.list_notebooks(debug=args.debug)

        if args.json:
            # Output as JSON
            output = []
            for nb in notebooks:
                # Handle datetime fields
                created_at = None
                modified_at = None

                if nb.created_at:
                    created_at = nb.created_at.isoformat() if hasattr(nb.created_at, 'isoformat') else str(nb.created_at)
                if nb.modified_at:
                    modified_at = nb.modified_at.isoformat() if hasattr(nb.modified_at, 'isoformat') else str(nb.modified_at)

                output.append({
                    "id": nb.id,
                    "title": nb.title,
                    "source_count": nb.source_count,
                    "is_owned": nb.is_owned,
                    "is_shared": nb.is_shared,
                    "created_at": created_at,
                    "modified_at": modified_at,
                })
            print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            if not notebooks:
                print("No notebooks found")
                return

            print(f"Found {len(notebooks)} notebook(s):\n")
            for nb in notebooks:
                status = "📗" if nb.is_owned else "📘"
                shared = " (shared)" if nb.is_shared else ""
                print(f"{status} {nb.title}{shared}")
                print(f"   ID: {nb.id}")
                print(f"   Sources: {nb.source_count}")
                if nb.modified_at:
                    if hasattr(nb.modified_at, 'strftime'):
                        print(f"   Modified: {nb.modified_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    else:
                        print(f"   Modified: {nb.modified_at}")
                print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
