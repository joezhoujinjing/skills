"""Search through processed email data."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def _load_emails(data_dir: Path, account: Optional[str] = None) -> list[dict]:
    """Load all emails with their latest decisions."""
    results = []

    # Determine which account dirs to scan
    if account:
        account_dirs = [data_dir / account]
        if not account_dirs[0].exists():
            print(f"Account not found: {account}")
            return []
    else:
        account_dirs = [d for d in data_dir.iterdir() if d.is_dir()]

    for acct_dir in account_dirs:
        emails_dir = acct_dir / "emails"
        if not emails_dir.exists():
            continue

        for date_dir in sorted(emails_dir.iterdir()):
            if not date_dir.is_dir():
                continue
            for msg_dir in date_dir.iterdir():
                if not msg_dir.is_dir():
                    continue

                email_file = msg_dir / "email.json"
                if not email_file.exists():
                    continue

                with open(email_file) as f:
                    email = json.load(f)

                # Load latest decision
                decisions_dir = msg_dir / "decisions"
                decision = None
                if decisions_dir.exists():
                    decision_files = sorted(decisions_dir.glob("*.json"))
                    if decision_files:
                        with open(decision_files[-1]) as f:
                            decision = json.load(f)

                email["_decision"] = decision
                email["_account"] = acct_dir.name
                results.append(email)

    return results


def _matches(email: dict, query: str) -> list[str]:
    """Check if email matches query. Returns list of matched field names."""
    q = query.lower()
    matched = []

    search_fields = {
        "from": email.get("from", ""),
        "to": email.get("to", ""),
        "subject": email.get("subject", ""),
        "snippet": email.get("snippet", ""),
        "body": email.get("body", ""),
    }

    # Also search decision fields
    decision = email.get("_decision")
    if decision:
        search_fields["category"] = decision.get("category", "")
        search_fields["reason"] = decision.get("reason", "")

    for field, value in search_fields.items():
        if value and q in value.lower():
            matched.append(field)

    return matched


def _parse_date(s: str) -> Optional[datetime]:
    """Parse YYYY-MM-DD date string."""
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return None


def _truncate(s: str, max_len: int) -> str:
    """Truncate string with ellipsis."""
    if len(s) <= max_len:
        return s
    return s[:max_len - 1] + "…"


def _extract_sender(from_field: str) -> str:
    """Extract readable sender name from 'Name <email>' format."""
    if "<" in from_field:
        name = from_field.split("<")[0].strip().strip('"')
        if name:
            return name
    return from_field


def search(skill_root: Path, args: list[str]):
    """Run email search."""
    # Parse args
    query = None
    account = None
    date_from = None
    date_to = None
    category = None
    action = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--account" and i + 1 < len(args):
            account = args[i + 1]
            i += 2
        elif arg == "--from" and i + 1 < len(args):
            date_from = _parse_date(args[i + 1])
            if not date_from:
                print(f"Invalid date format: {args[i + 1]} (use YYYY-MM-DD)")
                sys.exit(1)
            i += 2
        elif arg == "--to" and i + 1 < len(args):
            date_to = _parse_date(args[i + 1])
            if not date_to:
                print(f"Invalid date format: {args[i + 1]} (use YYYY-MM-DD)")
                sys.exit(1)
            i += 2
        elif arg == "--category" and i + 1 < len(args):
            category = args[i + 1]
            i += 2
        elif arg == "--action" and i + 1 < len(args):
            action = args[i + 1]
            i += 2
        elif not arg.startswith("--"):
            query = arg
            i += 1
        else:
            print(f"Unknown option: {arg}")
            sys.exit(1)

    if not query and not any([account, date_from, date_to, category, action]):
        print("Usage: python -m email_processor search <query> [options]")
        print()
        print("Options:")
        print("  --account <email>     Search specific account")
        print("  --from <YYYY-MM-DD>   Start date")
        print("  --to <YYYY-MM-DD>     End date")
        print("  --category <cat>      Filter by category (auto_archive, urgent, etc.)")
        print("  --action <act>        Filter by action (archive, review, trello)")
        sys.exit(1)

    # Load config to get storage path
    with open(skill_root / "config" / "config.json") as f:
        config = json.load(f)

    data_dir = skill_root / config["storage"]["base_path"]
    emails = _load_emails(data_dir, account)

    # Apply filters
    results = []
    for email in emails:
        # Date filter
        email_date = email.get("date", "")
        if email_date:
            try:
                dt = datetime.fromisoformat(email_date)
                if date_from and dt.replace(tzinfo=None) < date_from:
                    continue
                if date_to and dt.replace(tzinfo=None) > date_to.replace(hour=23, minute=59, second=59):
                    continue
            except ValueError:
                pass

        # Category/action filter
        decision = email.get("_decision")
        if category:
            if not decision or decision.get("category", "").lower() != category.lower():
                continue
        if action:
            if not decision or decision.get("action", "").lower() != action.lower():
                continue

        # Query match
        if query:
            matched_fields = _matches(email, query)
            if not matched_fields:
                continue
        else:
            matched_fields = []

        results.append((email, matched_fields))

    # Sort by date descending
    results.sort(key=lambda r: r[0].get("date", ""), reverse=True)

    # Display
    if not results:
        print("No results found.")
        return

    print(f"\n{'─' * 90}")
    print(f" {len(results)} results found" + (f" for \"{query}\"" if query else ""))
    print(f"{'─' * 90}")

    for idx, (email, matched_fields) in enumerate(results, 1):
        decision = email.get("_decision")
        date_str = email.get("date", "")[:10]
        sender = _extract_sender(email.get("from", "?"))
        subject = email.get("subject", "(no subject)")
        acct = email.get("_account", "?")

        cat = decision.get("category", "?") if decision else "?"
        act = decision.get("action", "?") if decision else "?"

        # Format line
        print(f"\n[{idx}] {_truncate(subject, 60)}")
        print(f"    {sender}  ·  {date_str}  ·  {acct}")
        print(f"    {act} / {cat}", end="")
        if matched_fields:
            print(f"  (matched: {', '.join(matched_fields)})", end="")
        print()

        # Show snippet preview if query matched in snippet
        if "snippet" in matched_fields:
            snippet = email.get("snippet", "")
            if snippet:
                print(f"    \"{_truncate(snippet, 80)}\"")

    print(f"\n{'─' * 90}\n")
