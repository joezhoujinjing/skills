"""File-based storage for email history.

Structure:
  data/
    <account>/
      emails/
        <YYYY-MM-DD>/
          <message_id>/
            email.json
            decisions/
              <session_id>.json
      sessions/
        <session_id>/
          session.json
          processed.jsonl
          actions.jsonl
      index/
        all-emails.jsonl
        by-sender.json
        stats.json
"""

import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

from ..models.email import Email, TriageDecision


class FileStorage:
    """File-based storage for email history and sessions."""

    def __init__(self, base_path: str, account: str, timezone: str = "America/Los_Angeles"):
        self.base = Path(base_path) / account
        self.tz = ZoneInfo(timezone)
        self.account = account

        # Generate session ID
        now = datetime.now(self.tz)
        tz_abbr = now.strftime('%Z')  # PST or PDT
        self.session_id = now.strftime(f'%Y-%m-%d_%H%M%S-{tz_abbr}')
        self.session_started = now

        # Ensure directories exist
        self.emails_dir = self.base / "emails"
        self.sessions_dir = self.base / "sessions" / self.session_id
        self.index_dir = self.base / "index"

        self.emails_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        # Session counters
        self._stats = {
            "auto_archived": 0,
            "auto_trello": 0,
            "reviewed": 0,
            "by_processor": {},
            "by_category": {},
            "by_action": {},
        }

    # --- Email storage ---

    def _email_dir(self, email: Email) -> Path:
        """Get date-organized directory for an email."""
        date_str = email.date.astimezone(self.tz).strftime('%Y-%m-%d')
        return self.emails_dir / date_str / email.message_id

    def save_email(self, email: Email):
        """Save email to canonical storage (one copy per email, ever)."""
        email_dir = self._email_dir(email)
        email_dir.mkdir(parents=True, exist_ok=True)

        email_file = email_dir / "email.json"

        # Only write if not already stored
        if not email_file.exists():
            data = {
                "message_id": email.message_id,
                "gmail_id": email.message_id,
                "thread_id": email.thread_id,
                "account": email.account,
                "from": email.from_addr,
                "to": email.to_addr,
                "cc": email.cc_addr,
                "subject": email.subject,
                "date": email.date.isoformat(),
                "snippet": email.snippet,
                "body": email.body,
                "labels": email.labels,
                "first_seen": self.session_id,
                "first_seen_at": datetime.now(self.tz).isoformat(),
            }
            email_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # --- Decision storage ---

    def save_decision(self, decision: TriageDecision, email: Optional[Email] = None,
                      trello_info: Optional[dict] = None):
        """Save triage decision for an email in this session."""
        if email:
            email_dir = self._email_dir(email)
        else:
            email_dir = self.emails_dir / decision.message_id
        decisions_dir = email_dir / "decisions"
        decisions_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "session_id": self.session_id,
            "timestamp": datetime.now(self.tz).isoformat(),
            "action": decision.action,
            "category": decision.category,
            "priority": decision.priority,
            "reason": decision.reason,
            "processor": decision.processor,
            "rule_name": decision.rule_name,
            "confidence": decision.confidence,
            "trello_suggestion": decision.trello_suggestion,
            "trello_card_id": trello_info.get("id") if trello_info else None,
            "trello_card_url": trello_info.get("url") if trello_info else None,
            "executed": True,
        }

        decision_file = decisions_dir / f"{self.session_id}.json"
        decision_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

        # Track stats
        self._stats["by_processor"][decision.processor] = self._stats["by_processor"].get(decision.processor, 0) + 1
        self._stats["by_category"][decision.category] = self._stats["by_category"].get(decision.category, 0) + 1
        self._stats["by_action"][decision.action] = self._stats["by_action"].get(decision.action, 0) + 1

    # --- Session logging ---

    def log_processed(self, message_id: str, action: str, auto: bool,
                      processor: str = "", trello_card_id: str = None):
        """Append to processed.jsonl for this session."""
        entry = {
            "timestamp": datetime.now(self.tz).isoformat(),
            "message_id": message_id,
            "action": action,
            "auto": auto,
            "processor": processor,
        }
        if trello_card_id:
            entry["trello_card_id"] = trello_card_id

        with open(self.sessions_dir / "processed.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_action(self, message_id: str, action: str, **kwargs):
        """Append user action to actions.jsonl for this session."""
        entry = {
            "timestamp": datetime.now(self.tz).isoformat(),
            "message_id": message_id,
            "action": action,
            **kwargs,
        }

        with open(self.sessions_dir / "actions.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")

    # --- Session completion ---

    def complete_session(self, total_processed: int, auto_archived: int,
                         auto_trello: int, reviewed: int):
        """Write session.json with final stats."""
        self._stats["auto_archived"] = auto_archived
        self._stats["auto_trello"] = auto_trello
        self._stats["reviewed"] = reviewed

        data = {
            "session_id": self.session_id,
            "account": self.account,
            "started_at": self.session_started.isoformat(),
            "completed_at": datetime.now(self.tz).isoformat(),
            "timezone": str(self.tz),
            "total_processed": total_processed,
            "stats": self._stats,
        }

        session_file = self.sessions_dir / "session.json"
        session_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # --- Index management ---

    def update_index(self, email: Email, decision: TriageDecision):
        """Append to global index."""
        # all-emails.jsonl (append)
        entry = {
            "message_id": email.message_id,
            "from": email.from_addr,
            "subject": email.subject,
            "date": email.date.isoformat(),
            "last_action": decision.action,
            "last_category": decision.category,
            "last_session": self.session_id,
            "last_updated": datetime.now(self.tz).isoformat(),
        }

        with open(self.index_dir / "all-emails.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")

    def update_sender_index(self, emails: list):
        """Update by-sender.json with batch of emails."""
        sender_file = self.index_dir / "by-sender.json"

        # Load existing
        if sender_file.exists():
            existing = json.loads(sender_file.read_text())
        else:
            existing = {}

        # Update
        for email in emails:
            sender = email.from_addr.lower()
            if sender not in existing:
                existing[sender] = {"message_ids": [], "count": 0, "last_seen": ""}
            if email.message_id not in existing[sender]["message_ids"]:
                existing[sender]["message_ids"].append(email.message_id)
                existing[sender]["count"] = len(existing[sender]["message_ids"])
            existing[sender]["last_seen"] = email.date.isoformat()

        sender_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

    def update_stats(self, total_processed: int):
        """Update global stats.json."""
        stats_file = self.index_dir / "stats.json"

        # Load existing
        if stats_file.exists():
            stats = json.loads(stats_file.read_text())
        else:
            stats = {
                "total_emails": 0,
                "total_sessions": 0,
                "by_action": {},
                "by_category": {},
            }

        # Update
        stats["total_emails"] += total_processed
        stats["total_sessions"] += 1
        stats["last_session"] = self.session_id
        stats["last_updated"] = datetime.now(self.tz).isoformat()
        stats["timezone"] = str(self.tz)

        for action, count in self._stats["by_action"].items():
            stats["by_action"][action] = stats["by_action"].get(action, 0) + count
        for category, count in self._stats["by_category"].items():
            stats["by_category"][category] = stats["by_category"].get(category, 0) + count

        stats_file.write_text(json.dumps(stats, indent=2, ensure_ascii=False))
