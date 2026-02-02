#!/usr/bin/env python3
"""Query a NotebookLM notebook (ask a question)."""

import argparse
import json
import re
import sys
from _client import get_client


def extract_citations(answer_text):
    """Extract inline citation markers [1], [2], etc. from answer text.

    Returns:
        List of unique citation numbers found in the text, sorted.
    """
    citation_nums = re.findall(r'\[(\d+)\]', answer_text)
    return sorted(set(int(num) for num in citation_nums))


def get_citation_sources(client, notebook_id, citation_numbers):
    """Attempt to map citation numbers to source titles.

    Args:
        client: NotebookLM client
        notebook_id: Notebook ID
        citation_numbers: List of citation numbers to map

    Returns:
        Dict mapping citation number to source info, or empty dict if mapping fails.
    """
    try:
        sources = client.get_notebook_sources_with_types(notebook_id)
        citation_map = {}

        for num in citation_numbers:
            idx = num - 1
            if idx < len(sources):
                src = sources[idx]
                title = src.get('title') if isinstance(src, dict) else getattr(src, 'title', 'Unknown')
                src_type = src.get('source_type_name') if isinstance(src, dict) else getattr(src, 'source_type_name', 'unknown')
                src_id = src.get('id') if isinstance(src, dict) else getattr(src, 'id', None)

                citation_map[num] = {
                    'number': num,
                    'title': title,
                    'type': src_type,
                    'source_id': src_id
                }

        return citation_map
    except Exception:
        # If we can't map citations, just return empty dict
        return {}


def main():
    parser = argparse.ArgumentParser(description="Query a NotebookLM notebook")
    parser.add_argument("notebook_id", help="Notebook ID")
    parser.add_argument("--question", "-q", required=True, help="Question to ask")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-citations", action="store_true", help="Don't fetch citation source mapping")
    args = parser.parse_args()

    client = get_client()

    try:
        result = client.query(args.notebook_id, args.question)

        if not result:
            print("Error: No response from notebook", file=sys.stderr)
            sys.exit(1)

        # Extract answer from result
        answer = None

        if isinstance(result, dict):
            answer = result.get("answer", "")
        elif isinstance(result, str):
            answer = result

        # Extract inline citations from the answer text
        citation_numbers = extract_citations(answer)

        # Optionally map citations to sources
        citations = []
        if citation_numbers and not args.no_citations:
            citation_map = get_citation_sources(client, args.notebook_id, citation_numbers)
            citations = [citation_map.get(num, {'number': num}) for num in citation_numbers]

        if args.json:
            output = {
                "question": args.question,
                "answer": answer,
                "citations": citations if citations else citation_numbers,
            }
            # Include conversation metadata if available
            if isinstance(result, dict):
                if 'conversation_id' in result:
                    output['conversation_id'] = result['conversation_id']
                if 'turn_number' in result:
                    output['turn_number'] = result['turn_number']

            print(json.dumps(output, indent=2))
        else:
            print(f"Q: {args.question}\n")
            print(f"A: {answer}")

            if citation_numbers:
                print(f"\n{len(citation_numbers)} citation(s) referenced: {citation_numbers}")

                if citations:
                    print("\nCitation sources:")
                    for cite in citations:
                        if 'title' in cite:
                            print(f"  [{cite['number']}] {cite['title']} ({cite.get('type', 'unknown')})")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
