"""Email and decision data models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import List, Optional, Literal


@dataclass
class Email:
    """Email data model."""
    message_id: str
    thread_id: str
    account: str  # 'work' or 'personal'

    from_addr: str
    to_addr: str
    cc_addr: Optional[str]
    subject: str
    date: datetime
    snippet: str
    body: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    attachments: List[dict] = field(default_factory=list)
    # [{"filename": "invoice.pdf", "mimeType": "application/pdf",
    #   "size": 12345, "attachmentId": "ANGjdJ..."}]

    fetched_at: datetime = field(default_factory=datetime.now)


@dataclass
class TriageDecision:
    """Processing decision for an email."""
    email_index: int
    message_id: str

    # Decision
    action: Literal["archive", "review", "trello"]
    category: str  # urgent, customer, internal, newsletter, etc.
    priority: int  # 0=urgent, 5=spam
    reason: str

    # Metadata
    processor: Literal["rules", "llm", "user"]
    rule_name: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0

    # Trello suggestion (if action="trello" or "review" with suggested card)
    trello_suggestion: Optional[dict] = None
    # {
    #   "title": "Task title",
    #   "action": "Next action description",
    #   "due_days": 1-7,
    #   "board": "multifi" | "personal" | "nexus" | "clinview" | "huiya" | "inbox"
    # }


@dataclass
class ReviewItem:
    """Email + decision for review UI."""
    index: int
    email: Email
    decision: TriageDecision

    def summary_line(self) -> str:
        """One-line summary for index view."""
        from_name = self._extract_name(self.email.from_addr)
        date_str = self._format_date(self.email.date)

        # Truncate subject to 60 chars
        subject = self.email.subject[:60]
        if len(self.email.subject) > 60:
            subject += "..."

        return f"[{self.index}] {subject}\n    {from_name} · {date_str}"

    def _extract_name(self, email_addr: str) -> str:
        """Extract sender name from email address."""
        if '<' in email_addr and '>' in email_addr:
            return email_addr.split('<')[0].strip()
        return email_addr.split('@')[0]

    def _format_date(self, dt: datetime) -> str:
        """Format date relative to now (Pacific Time)."""
        pacific = ZoneInfo("America/Los_Angeles")

        # Ensure dt is timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Convert to Pacific Time
        dt_pacific = dt.astimezone(pacific)
        now_pacific = datetime.now(pacific)

        diff = now_pacific - dt_pacific

        if diff.days == 0:
            return f"Today {dt_pacific.strftime('%I:%M %p')}"
        elif diff.days == 1:
            return f"Yesterday {dt_pacific.strftime('%I:%M %p')}"
        elif diff.days < 7:
            return dt_pacific.strftime("%a %I:%M %p")  # Mon 3:15 PM
        else:
            return dt_pacific.strftime("%b %d %I:%M %p")  # Feb 14 3:15 PM
