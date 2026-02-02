#!/usr/bin/env python3
"""Delete all NotebookLM notebooks that have 0 sources."""

import sys
from _client import get_client


def main():
    client = get_client()

    try:
        notebooks = client.list_notebooks()
        zero_sources = [nb for nb in notebooks if nb.source_count == 0]

        if not zero_sources:
            print("No notebooks with 0 sources found.")
            return

        print(f"Deleting {len(zero_sources)} notebook(s) with 0 sources:\n")
        for nb in zero_sources:
            shared = " (shared)" if nb.is_shared else ""
            try:
                client.delete_notebook(nb.id)
                print(f"  Deleted: {nb.title}{shared} ({nb.id})")
            except Exception as e:
                print(f"  Failed: {nb.title}{shared} — {e}", file=sys.stderr)
        print("\nDone.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
