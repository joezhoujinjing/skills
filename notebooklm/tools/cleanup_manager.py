#!/usr/bin/env python3
"""Cleanup NotebookLM skill data cache."""

import argparse
import shutil
from pathlib import Path

from _utils import DATA_DIR


def cleanup(confirm: bool) -> dict:
    if not DATA_DIR.exists():
        return {"status": "ok", "message": "No data directory"}
    if not confirm:
        return {"status": "preview", "path": str(DATA_DIR)}
    shutil.rmtree(DATA_DIR)
    return {"status": "deleted", "path": str(DATA_DIR)}


def main():
    parser = argparse.ArgumentParser(description="Cleanup NotebookLM data directory")
    parser.add_argument("--confirm", action="store_true", help="Confirm deletion")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = cleanup(args.confirm)
    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["status"] == "preview":
            print(f"Would remove: {result['path']}")
        else:
            print(f"Removed: {result['path']}")


if __name__ == "__main__":
    main()
