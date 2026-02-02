#!/usr/bin/env python3
"""List sources in a NotebookLM notebook."""

import argparse
import json
import sys
from _client import get_client


def main():
    parser = argparse.ArgumentParser(description="List sources in a NotebookLM notebook")
    parser.add_argument("notebook_id", help="Notebook ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    client = get_client()

    try:
        sources = client.get_notebook_sources_with_types(args.notebook_id)

        if not sources:
            if args.json:
                print(json.dumps([]))
            else:
                print("No sources found in this notebook")
            return

        if args.json:
            print(json.dumps(sources, indent=2))
        else:
            print(f"Found {len(sources)} source(s):\n")
            for src in sources:
                src_id = src.get("id", "")
                title = src.get("title", "Untitled")
                source_type = src.get("type", "unknown")
                status = src.get("status", 0)

                status_map = {
                    1: "⏳ processing",
                    2: "✅ ready",
                    3: "❌ error",
                    5: "🔄 preparing",
                }
                status_str = status_map.get(status, f"status={status}")

                print(f"📄 {title}")
                print(f"   ID: {src_id}")
                print(f"   Type: {source_type}")
                print(f"   Status: {status_str}")
                print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
