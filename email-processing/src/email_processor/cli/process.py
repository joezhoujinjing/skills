"""Main email processing orchestrator."""

import asyncio
import json
import yaml
from pathlib import Path
from collections import Counter

from ..core import GmailClient, RulesEngine, GeminiTriage, TrelloClient
from ..storage.file_storage import FileStorage
from ..models.email import Email, TriageDecision, ReviewItem
from .review import ReviewInterface


class EmailProcessor:
    """Main triage orchestrator."""

    @staticmethod
    def _find_skill_root() -> Path:
        """Find the skill root by locating SKILL.md."""
        path = Path(__file__).resolve().parent
        while path != path.parent:
            if (path / "SKILL.md").exists():
                return path
            path = path.parent
        raise FileNotFoundError("Could not find SKILL.md in any parent directory")

    def __init__(self, email: str, skill_root: Path = None):
        self.email = email

        # Resolve skill root
        if skill_root is None:
            skill_root = self._find_skill_root()

        # Load configs
        config_dir = skill_root / "config"

        with open(config_dir / "config.json") as f:
            config = json.load(f)
        with open(config_dir / "rules.yaml") as f:
            rules_config = yaml.safe_load(f)

        # Store global config settings
        self.config = config
        self.timezone = config['timezone']
        self.storage_base = skill_root / config['storage']['base_path']
        self.confidence_threshold = config['processing']['auto_trello_confidence_threshold']

        # Get account config using email as key
        self.account_config = config['accounts'][email]
        self.account_config['email'] = email
        self.account_config['account_type'] = email

        # Initialize components
        self.gmail = GmailClient(self.account_config)
        self.rules = RulesEngine(rules_config, email)
        self.llm = GeminiTriage(self.account_config, config.get('llm', {}))
        self.trello = TrelloClient(
            config.get('trello', {}),
            default_board=self.account_config.get('default_trello_board', 'inbox')
        )
        self.storage = FileStorage(
            base_path=str(self.storage_base),
            account=email,
            timezone=self.timezone,
        )

    async def process(self, limit: int = None):
        """Main triage workflow."""
        print(f"✅ Processing account: {self.email}")
        print(f"   Session: {self.storage.session_id}")

        # Step 1: Fetch emails
        print("\n🔍 Fetching emails from Gmail...")
        emails = await self.gmail.fetch_inbox(max_results=limit)
        print(f"✅ Found {len(emails)} emails in inbox")

        if not emails:
            print("✨ Inbox is empty! Nothing to process.")
            return

        # Step 2: Apply rules
        print("\n📊 Processing with rules engine...")
        decisions = []
        needs_llm = []

        for idx, email in enumerate(emails):
            match = self.rules.evaluate(email)

            if match.action == "llm_triage":
                needs_llm.append((idx, email))
            else:
                decision = TriageDecision(
                    email_index=idx,
                    message_id=email.message_id,
                    action=match.action,
                    category=match.category,
                    priority=match.priority,
                    reason=match.reason,
                    processor="rules",
                    rule_name=match.rule_name,
                    confidence=match.confidence
                )
                decisions.append(decision)

        # Step 3: LLM triage for unclear emails
        if needs_llm:
            print(f"\n🤖 LLM triaging {len(needs_llm)} unclear emails...")
            llm_emails = [email for _, email in needs_llm]
            llm_decisions = await self.llm.triage_batch(llm_emails)

            for (idx, email), llm_decision in zip(needs_llm, llm_decisions):
                llm_decision.email_index = idx
                llm_decision.message_id = email.message_id
                decisions.append(llm_decision)

        # Sort decisions by email index
        decisions.sort(key=lambda d: d.email_index)

        # Step 4: Execute auto-actions
        print("\n📦 Executing auto-actions...")

        to_archive = []
        to_trello = []
        to_review = []

        for email, decision in zip(emails, decisions):
            if decision.action == "archive":
                to_archive.append((email, decision))
            elif decision.action == "trello" and decision.confidence > self.confidence_threshold:
                to_trello.append((email, decision))
            else:
                to_review.append((email, decision))

        # Batch archive
        if to_archive:
            print(f"   Archiving {len(to_archive)} emails...")
            await self.gmail.archive_batch([e.message_id for e, _ in to_archive])
            print(f"   ✅ Archived {len(to_archive)} emails")

            archive_decisions = [d for _, d in to_archive]
            categories = Counter(d.category for d in archive_decisions)
            for cat, count in categories.most_common():
                print(f"      ├─ {cat.title()}: {count}")

        # Auto-create Trello cards for high-confidence items
        if to_trello:
            print(f"   Creating {len(to_trello)} Trello cards...")
            for email, decision in to_trello:
                try:
                    card_info = await self.trello.create_card_from_email(
                        email, self.email,
                        decision.category, decision.priority,
                        decision.trello_suggestion
                    )
                    await self.gmail.archive(email.message_id)

                    # Save with Trello info
                    self.storage.save_email(email)
                    self.storage.save_decision(decision, email=email, trello_info=card_info)
                    self.storage.log_processed(
                        email.message_id, "trello", auto=True,
                        processor=decision.processor,
                        trello_card_id=card_info.get("id")
                    )

                except Exception as e:
                    print(f"      ❌ Failed to create card: {e}")

        # Step 5: Save all emails & decisions to file storage
        print("\n💾 Saving to file storage...")
        for email, decision in zip(emails, decisions):
            self.storage.save_email(email)
            if decision.action != "trello":
                self.storage.save_decision(decision, email=email)
                self.storage.log_processed(
                    email.message_id, decision.action,
                    auto=(decision.action == "archive"),
                    processor=decision.processor
                )
            self.storage.update_index(email, decision)

        # Update global indexes
        self.storage.update_sender_index(emails)
        print(f"✅ Saved {len(emails)} emails to {self.storage.base}")

        # Step 6: Interactive review
        if to_review:
            print(f"\n👀 {len(to_review)} emails need your review")

            review_items = [
                ReviewItem(idx + 1, email, decision)
                for idx, (email, decision) in enumerate(to_review)
            ]

            interface = ReviewInterface(
                review_items, self.gmail, self.trello,
                self.email, self.storage
            )
            interface.show_list()

            while interface.items:
                try:
                    command = input("\n> ").strip()
                    should_continue = interface.handle_command(command)
                    if not should_continue:
                        break
                except (KeyboardInterrupt, EOFError):
                    print("\n\n⚠️  Interrupted by user")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")

        # Step 7: Complete session
        self.storage.complete_session(
            total_processed=len(emails),
            auto_archived=len(to_archive),
            auto_trello=len(to_trello),
            reviewed=len(to_review),
        )
        self.storage.update_stats(len(emails))

        # Final summary
        print("\n" + "=" * 80)
        print("🎉 TRIAGE SESSION COMPLETE")
        print("=" * 80)
        print(f"Session: {self.storage.session_id}")
        print(f"Total processed: {len(emails)}")
        print(f"  ✅ Auto-archived: {len(to_archive)}")
        print(f"  📋 Trello cards created: {len(to_trello)}")
        print(f"  👀 Reviewed: {len(to_review)}")
        print(f"  📁 Saved to: {self.storage.sessions_dir}")

        # Check inbox status
        counts = await self.gmail.count_inbox()
        print("\n📊 EMAIL STATUS REPORT")
        print(f"   ├─ Inbox (Total): {counts['inbox_total']}")
        print(f"   └─ Global Unread: {counts['global_unread']}")

        if counts['inbox_total'] == 0:
            print("\n🎉 INBOX ZERO ACHIEVED! 🎉")
        else:
            print(f"\n📮 {counts['inbox_total']} emails remaining in inbox")
