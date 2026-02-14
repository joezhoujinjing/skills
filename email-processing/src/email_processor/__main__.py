"""Main CLI entry point."""

import sys
import asyncio
import json
from pathlib import Path

from .cli.process import EmailProcessor


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
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python -m email_processor <email>")
        print()
        print("  Examples:")
        print("    python -m email_processor joe@multifi.ai")
        print("    python -m email_processor joezhoujinjing@gmail.com")
        sys.exit(1)

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
