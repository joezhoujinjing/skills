"""Main CLI entry point."""

import sys
import asyncio
import json
from pathlib import Path

from .cli.process import EmailProcessor
from .cli.search import search


def _find_skill_root() -> Path:
    """Find the skill root by locating SKILL.md."""
    path = Path(__file__).resolve().parent
    while path != path.parent:
        if (path / "SKILL.md").exists():
            return path
        path = path.parent
    raise FileNotFoundError("Could not find SKILL.md in any parent directory")


def main():
    """Main entry point for email processing."""
    if len(sys.argv) < 2:
        print("Usage: python -m email_processor <email> [limit]")
        print("       python -m email_processor search <query> [options]")
        print()
        print("  Examples:")
        print("    python -m email_processor joe@multifi.ai")
        print("    python -m email_processor search \"trello\" --account joe@multifi.ai")
        sys.exit(1)

    # Route to search subcommand
    if sys.argv[1] == "search":
        skill_root = _find_skill_root()
        search(skill_root, sys.argv[2:])
        return

    email = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else None

    # Validate email exists in config
    skill_root = _find_skill_root()
    with open(skill_root / "config" / "config.json") as f:
        config = json.load(f)

    if email not in config['accounts']:
        print(f"❌ Email not found in configuration: {email}")
        print()
        print("Available emails:")
        for account_email in config['accounts'].keys():
            print(f"  - {account_email}")
        sys.exit(1)

    # Run processor with email as account key
    processor = EmailProcessor(email, skill_root=skill_root)
    asyncio.run(processor.process(limit=limit))


if __name__ == "__main__":
    main()
