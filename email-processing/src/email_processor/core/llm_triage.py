"""LLM-based email triage using LangChain + Gemini with structured output."""

import asyncio
from typing import List, Optional, Literal

from pydantic import BaseModel, Field

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("⚠️  Warning: langchain-google-genai not installed. Run: pip install langchain-google-genai")
    ChatGoogleGenerativeAI = None

from ..models.email import Email, TriageDecision
from .secrets import resolve_secret


# --- Pydantic models for structured output ---

class TrelloSuggestion(BaseModel):
    """Suggested Trello card details."""
    title: str = Field(description="Short card title summarizing the task")
    action: str = Field(description="What needs to be done")
    due_days: int = Field(default=3, description="Days until due (1-7)")
    board: Literal["multifi", "personal", "nexus", "clinview", "huiya", "inbox"] = Field(
        description="Which Trello board to add the card to"
    )


class EmailDecision(BaseModel):
    """Triage decision for a single email."""
    email_index: int = Field(description="Index of the email being triaged")
    action: Literal["archive", "review", "trello"] = Field(
        description="archive=low-value, review=needs human, trello=actionable task"
    )
    category: str = Field(description="Email category: urgent, customer, internal, newsletter, recruiting, social, event, receipt, other")
    priority: int = Field(default=3, description="0=urgent to 5=spam")
    reason: str = Field(description="One sentence explaining the decision")
    confidence: float = Field(default=0.8, description="Confidence score 0.0 to 1.0")
    trello_suggestion: Optional[TrelloSuggestion] = Field(
        default=None, description="Trello card details (required when action=trello)"
    )


class TriageBatchResult(BaseModel):
    """Batch of triage decisions."""
    decisions: List[EmailDecision] = Field(description="One decision per email")


# --- Main triage class ---

class GeminiTriage:
    """LLM triage using LangChain + Gemini with structured output."""

    def __init__(self, account_config: dict, llm_config: dict):
        self.account_config = account_config
        self.llm_config = llm_config
        self.model_name = llm_config.get('model', 'gemini-3-flash-preview')
        self.temperature = llm_config.get('temperature', 0.3)
        self.max_output_tokens = llm_config.get('max_output_tokens', 4096)
        self.batch_size = llm_config.get('batch_size', 10)
        self.rate_limit_seconds = llm_config.get('rate_limit_seconds', 6)

        # Configure LangChain + Gemini
        if ChatGoogleGenerativeAI:
            api_key = resolve_secret(llm_config.get('api_key', 'gsm:nexus-hub-google-api-key'))
            if api_key:
                llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    google_api_key=api_key,
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens,
                )
                self.structured_llm = llm.with_structured_output(TriageBatchResult)
            else:
                self.structured_llm = None
        else:
            self.structured_llm = None

    async def triage_batch(self, emails: List[Email]) -> List[TriageDecision]:
        """Triage emails in batches with rate limiting."""
        if not self.structured_llm:
            print("⚠️  Gemini not configured, skipping LLM triage")
            return self._fallback_decisions(emails)

        # Split into batches
        batches = [emails[i:i+self.batch_size] for i in range(0, len(emails), self.batch_size)]

        all_decisions = []
        for batch_idx, batch in enumerate(batches):
            if batch_idx > 0:
                await asyncio.sleep(self.rate_limit_seconds)

            print(f"   Batch {batch_idx + 1}/{len(batches)} ({len(batch)} emails)...")
            batch_decisions = await self._triage_single_batch(batch, batch_idx * self.batch_size)
            all_decisions.extend(batch_decisions)

        return all_decisions

    async def _triage_single_batch(self, emails: List[Email],
                                   start_index: int) -> List[TriageDecision]:
        """Process single batch with structured output."""
        prompt = self._build_prompt(emails, start_index)

        try:
            # Run sync LangChain call in executor
            loop = asyncio.get_event_loop()
            result: TriageBatchResult = await loop.run_in_executor(
                None,
                lambda: self.structured_llm.invoke(prompt)
            )

            # Convert Pydantic models to TriageDecision dataclasses
            parsed = []
            for d in result.decisions:
                try:
                    local_idx = d.email_index - start_index
                    if 0 <= local_idx < len(emails):
                        email = emails[local_idx]
                    else:
                        continue

                    trello_dict = None
                    if d.trello_suggestion:
                        trello_dict = d.trello_suggestion.model_dump()

                    parsed.append(TriageDecision(
                        email_index=d.email_index,
                        message_id=email.message_id,
                        action=d.action,
                        category=d.category,
                        priority=d.priority,
                        reason=d.reason,
                        processor='llm',
                        confidence=d.confidence,
                        trello_suggestion=trello_dict
                    ))
                except Exception as e:
                    print(f"   ⚠️  Skipping malformed decision: {e}")

            # Fill in any missing decisions
            processed_indices = {d.email_index for d in parsed}
            for i in range(len(emails)):
                if start_index + i not in processed_indices:
                    parsed.append(TriageDecision(
                        email_index=start_index + i,
                        message_id=emails[i].message_id,
                        action='review',
                        category='other',
                        priority=3,
                        reason='LLM did not return decision for this email',
                        processor='llm',
                        confidence=0.0
                    ))

            parsed.sort(key=lambda d: d.email_index)
            return parsed

        except Exception as e:
            print(f"   ❌ LLM error: {e}")
            return self._fallback_decisions(emails, start_index)

    def _build_prompt(self, emails: List[Email], start_index: int) -> str:
        """Build triage prompt."""
        account = self.account_config['email']
        internal_domains = self.account_config.get('internal_domains', [])

        emails_text = []
        for idx, email in enumerate(emails):
            emails_text.append(f"""
EMAIL {start_index + idx}:
From: {email.from_addr}
To: {email.to_addr}
Subject: {email.subject}
Date: {email.date.strftime('%Y-%m-%d %H:%M')}
Preview: {email.snippet[:250]}
---""")

        return f"""You are an expert email triage assistant. Analyze {len(emails)} emails and return categorization decisions.

USER CONTEXT:
- Account: {account}
- Internal domains: {internal_domains}

TRELLO BOARDS (6 available):
1. **multifi** - Work/company tasks, customer issues, HR/payroll, internal team work
2. **personal** - Personal life (family, health, home, school, hobbies)
3. **nexus** - Nexus project-specific tasks and issues
4. **clinview** - ClinView project-specific tasks and issues
5. **huiya** - Huiya project-specific tasks and issues
6. **inbox** - Default for unclear/ambiguous emails (catch-all)

BOARD SELECTION RULES:
- Emails mentioning "nexus", "nexus API", "nexus backend" → **nexus** board
- Emails mentioning "clinview", "clinical view" → **clinview** board
- Emails mentioning "huiya" → **huiya** board
- Emails from @multifi.ai or about MultiFi work → **multifi** board
- Personal life (family, school, health, home) → **personal** board
- When unclear which board → **inbox** board

CATEGORIES:
- urgent, customer, internal, newsletter, recruiting, social, event, receipt, other

ACTIONS:
- archive: Low-value content (newsletters, receipts, notifications, marketing)
- review: Needs human decision (unclear, ambiguous)
- trello: Actionable task >2min (create a Trello card)

PRIORITY: 0 (urgent) to 5 (spam)

EMAILS:
{chr(10).join(emails_text)}

Return one decision per email (email_index {start_index} through {start_index + len(emails) - 1})."""

    def _fallback_decisions(self, emails: List[Email],
                           start_index: int = 0) -> List[TriageDecision]:
        """Fallback when LLM fails."""
        return [
            TriageDecision(
                email_index=start_index + i,
                message_id=email.message_id,
                action='review',
                category='llm_error',
                priority=3,
                reason='LLM unavailable - needs manual review',
                processor='llm',
                confidence=0.0
            )
            for i, email in enumerate(emails)
        ]
