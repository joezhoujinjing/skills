#!/usr/bin/env python3
"""Create a new NotebookLM notebook."""

import argparse
import json
import sys
from _client import get_client


def main():
    parser = argparse.ArgumentParser(description="Create a new NotebookLM notebook")
    parser.add_argument("--title", required=True, help="Notebook title")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    client = get_client()

    try:
        notebook = client.create_notebook(title=args.title)

        if not notebook:
            print("Error: Failed to create notebook", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps({
                "id": notebook.id,
                "title": notebook.title,
                "source_count": notebook.source_count,
            }, indent=2))
        else:
            print(f"Created notebook: {notebook.title}")
            print(f"ID: {notebook.id}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
