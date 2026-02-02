#!/usr/bin/env python3
"""Query a NotebookLM notebook (ask a question)."""

import argparse
import json
import sys
from _client import get_client


def main():
    parser = argparse.ArgumentParser(description="Query a NotebookLM notebook")
    parser.add_argument("notebook_id", help="Notebook ID")
    parser.add_argument("--question", "-q", required=True, help="Question to ask")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    client = get_client()

    try:
        result = client.query(args.notebook_id, args.question)

        if not result:
            print("Error: No response from notebook", file=sys.stderr)
            sys.exit(1)

        # Extract answer from result
        answer = None
        citations = []

        if isinstance(result, dict):
            answer = result.get("answer", "")
            citations = result.get("citations", [])
        elif isinstance(result, str):
            answer = result

        if args.json:
            print(json.dumps({
                "question": args.question,
                "answer": answer,
                "citations": citations,
            }, indent=2))
        else:
            print(f"Q: {args.question}\n")
            print(f"A: {answer}")
            if citations:
                print(f"\nCitations: {len(citations)} source(s) referenced")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
