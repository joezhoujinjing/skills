"""Structured rules engine for email categorization."""

import re
from typing import Optional
from dataclasses import dataclass

from ..models.email import Email, TriageDecision


@dataclass
class RuleMatch:
    """Result of rule evaluation."""
    matched: bool
    rule_name: str
    category: str
    subcategory: Optional[str]
    priority: int
    action: str  # archive, review, trello
    reason: str
    confidence: float


class RulesEngine:
    """Evaluates emails against structured rules."""

    def __init__(self, rules_config: dict, account: str):
        self.config = rules_config
        self.account = account
        self.categories = rules_config.get('categories', {})

    def evaluate(self, email: Email) -> RuleMatch:
        """
        Evaluate email against all rules in priority order.
        Returns first match or 'needs LLM' if no match.
        """
        # Sort categories by priority
        sorted_categories = sorted(
            self.categories.items(),
            key=lambda x: x[1].get('priority', 99)
        )

        for category_name, category_config in sorted_categories:
            # Check account restriction
            if 'account' in category_config and category_config['account'] != self.account:
                continue

            # Evaluate rules in this category
            for rule in category_config.get('rules', []):
                if self._match_rule(email, rule):
                    return RuleMatch(
                        matched=True,
                        rule_name=rule.get('name', 'unnamed'),
                        category=category_name,
                        subcategory=None,
                        priority=category_config.get('priority', 99),
                        action=category_config.get('action', 'review'),
                        reason=f"Matched rule: {category_name}.{rule.get('name', 'unnamed')}",
                        confidence=1.0
                    )

            # Check subcategories (for auto_archive)
            subcategories = category_config.get('subcategories', {})
            for subcat_name, subcat_rules in subcategories.items():
                for rule in subcat_rules:
                    if self._match_rule(email, rule):
                        return RuleMatch(
                            matched=True,
                            rule_name=rule.get('name', 'unnamed'),
                            category=category_name,
                            subcategory=subcat_name,
                            priority=category_config.get('priority', 99),
                            action=category_config.get('action', 'archive'),
                            reason=f"Matched rule: {category_name}.{subcat_name}.{rule.get('name', 'unnamed')}",
                            confidence=1.0
                        )

        # No match - needs LLM triage
        return RuleMatch(
            matched=False,
            rule_name="no_match",
            category="unclear",
            subcategory=None,
            priority=99,
            action="llm_triage",
            reason="No rule match - needs LLM analysis",
            confidence=0.0
        )

    def _match_rule(self, email: Email, rule: dict) -> bool:
        """Evaluate a single rule against an email."""
        rule_type = rule.get('type')

        if rule_type == 'subject_contains':
            text = email.subject.lower()
            patterns = rule.get('patterns', [])
            case_sensitive = rule.get('case_sensitive', False)

            # Defensive: filter out non-string patterns (in case of malformed YAML)
            patterns = [p for p in patterns if isinstance(p, str)]

            if not case_sensitive:
                patterns = [p.lower() for p in patterns]
            else:
                text = email.subject

            matches = any(pattern in text for pattern in patterns)

            # Check exceptions
            if matches and 'exceptions' in rule:
                for exception in rule['exceptions']:
                    if self._match_rule(email, exception):
                        return False

            return matches

        elif rule_type == 'subject_regex':
            pattern = rule.get('pattern', '')
            return bool(re.search(pattern, email.subject, re.IGNORECASE))

        elif rule_type == 'from_domain':
            domain = self._extract_domain(email.from_addr)
            pattern = rule.get('pattern', '')
            patterns = rule.get('patterns', [pattern])

            # Defensive: filter out non-string patterns
            patterns = [p for p in patterns if isinstance(p, str)]

            matches = any(p in domain for p in patterns)

            # Check exceptions
            if matches and 'exceptions' in rule:
                for exception in rule['exceptions']:
                    if self._match_rule(email, exception):
                        return False

            return matches

        elif rule_type == 'from_sender':
            patterns = rule.get('patterns', [])

            # Defensive: filter out non-string patterns
            patterns = [p for p in patterns if isinstance(p, str)]

            sender_lower = email.from_addr.lower()
            return any(pattern.lower() in sender_lower for pattern in patterns)

        elif rule_type == 'all_of':
            # AND logic
            sub_rules = rule.get('rules', [])
            return all(self._match_rule(email, sub_rule) for sub_rule in sub_rules)

        elif rule_type == 'any_of':
            # OR logic
            sub_rules = rule.get('rules', [])
            return any(self._match_rule(email, sub_rule) for sub_rule in sub_rules)

        return False

    def _extract_domain(self, email_addr: str) -> str:
        """Extract domain from email address."""
        # Handle "Name <email@domain.com>" format
        if '<' in email_addr and '>' in email_addr:
            email_addr = email_addr.split('<')[1].split('>')[0]

        return email_addr.split('@')[-1] if '@' in email_addr else ''
