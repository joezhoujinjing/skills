"""Index-based review interface."""

from typing import List, Optional
from collections import defaultdict

from ..models.email import ReviewItem
from ..storage.file_storage import FileStorage


class ReviewInterface:
    """Index-based review interface with one-step actions."""

    def __init__(self, items: List[ReviewItem], gmail_client, trello_client,
                 account: str, storage: Optional[FileStorage] = None):
        self.original_items = items.copy()
        self.items = items
        self.gmail = gmail_client
        self.trello = trello_client
        self.account = account
        self.storage = storage

        # Group by priority
        self.urgent = [i for i in items if i.decision.priority == 0]
        self.important = [i for i in items if 1 <= i.decision.priority <= 2]
        self.other = [i for i in items if i.decision.priority >= 3]

    def show_list(self):
        """Display indexed email list."""
        print("━" * 80)
        print("👀 EMAILS NEEDING REVIEW")
        print("━" * 80)

        if self.urgent:
            print(f"\n🔴 URGENT ({len(self.urgent)} emails) - Priority 0\n")
            for item in self.urgent:
                print(item.summary_line())
                if item.decision.trello_suggestion:
                    print(f"    💡 Suggested: Trello card")
                print()

        if self.important:
            print(f"\n🟡 IMPORTANT ({len(self.important)} emails) - Priority 1-2\n")
            for item in self.important:
                print(item.summary_line())
                print()

        if self.other:
            print(f"\n🟢 OTHER ({len(self.other)} emails) - Priority 3+\n")
            # Show first 5, summarize rest
            for item in self.other[:5]:
                print(item.summary_line())
                print()

            if len(self.other) > 5:
                remaining = len(self.other) - 5
                indices = [str(i.index) for i in self.other[5:]]
                print(f"[{', '.join(indices[:5])}{'...' if len(indices) > 5 else ''}] ... ({remaining} more)")
                print()

        print("━" * 80)
        print("QUICK ACTIONS")
        print("━" * 80)
        print("Commands:")
        print("  <numbers>              Review emails (e.g., '1 2 5' or '1-4')")
        print("  archive <range>        Archive (e.g., 'archive 13-23')")
        print("  trello <range>         Create Trello cards (e.g., 'trello 1-4')")
        print("  show <category>        Filter (urgent/important/other)")
        print("  list                   Show this list again")
        print("  done                   Finish session")
        print("━" * 80)

    def handle_command(self, command: str) -> bool:
        """
        Parse and execute command.
        Returns: True if should continue, False if done.
        """
        import asyncio

        parts = command.strip().split()

        if not parts:
            return True

        cmd = parts[0].lower()

        # Parse indices
        if cmd.isdigit() or cmd in ['archive', 'trello']:
            if cmd.isdigit():
                # Direct numbers: "1 2 5" or "1-4"
                indices = self._parse_indices(command)
                asyncio.run(self._review_detailed(indices))
            elif cmd == 'archive':
                indices = self._parse_indices(' '.join(parts[1:]))
                asyncio.run(self._bulk_archive(indices))
            elif cmd == 'trello':
                indices = self._parse_indices(' '.join(parts[1:]))
                asyncio.run(self._bulk_trello(indices))

        elif cmd == 'show':
            category = parts[1] if len(parts) > 1 else None
            self._filter_category(category)

        elif cmd == 'list':
            self.show_list()

        elif cmd == 'done':
            self._finish_session()
            return False

        else:
            print(f"❌ Unknown command: {cmd}")

        return True

    def _parse_indices(self, text: str) -> List[int]:
        """Parse index numbers or ranges."""
        indices = []
        parts = text.replace(',', ' ').split()

        for part in parts:
            if '-' in part:
                # Range: 1-4
                try:
                    start, end = part.split('-')
                    indices.extend(range(int(start), int(end) + 1))
                except ValueError:
                    pass
            elif part.isdigit():
                indices.append(int(part))

        return sorted(set(indices))

    async def _review_detailed(self, indices: List[int]):
        """Show detailed view of selected emails."""
        items = [i for i in self.items if i.index in indices]

        for idx, item in enumerate(items, 1):
            print("\n" + "━" * 80)
            print(f"📧 EMAIL [{idx}/{len(items)}] - Index {item.index}")
            print("━" * 80)
            print(f"From: {item.email.from_addr}")
            print(f"Subject: {item.email.subject}")
            print(f"Date: {item.email.date.strftime('%Y-%m-%d %I:%M %p')}")
            print(f"Category: {item.decision.category.title()} (Priority {item.decision.priority})")
            print("━" * 80)
            print("SNIPPET:")
            print(item.email.snippet)
            print("━" * 80)

            if item.decision.trello_suggestion:
                print("💡 SUGGESTED TRELLO CARD:")
                print(f"   Title: {item.decision.trello_suggestion['title']}")
                print(f"   Action: {item.decision.trello_suggestion['action']}")
                print(f"   Due: {item.decision.trello_suggestion['due_days']} days")
                print(f"   Board: {item.decision.trello_suggestion.get('board', 'default')}")
                print("━" * 80)

            print("ACTIONS:")
            print("  1. Create Trello card" + (" (recommended)" if item.decision.trello_suggestion else ""))
            print("  2. Archive")
            print("  3. Show full email")
            print("  4. Skip")
            print("  back. Return to list")

            choice = input("\n> ").strip()

            if choice == '1':
                await self._create_trello_card(item)
            elif choice == '2':
                await self._archive_email(item)
            elif choice == '3':
                self._show_full_email(item)
                # Ask again
                await self._review_detailed([item.index])
            elif choice == '4':
                print("⏭️  Skipped")
            elif choice == 'back':
                break

    async def _bulk_archive(self, indices: List[int]):
        """Archive multiple emails at once."""
        items = [i for i in self.items if i.index in indices]

        print(f"\nArchiving {len(items)} emails...")
        message_ids = [i.email.message_id for i in items]

        # Batch archive via Gmail API
        await self.gmail.archive_batch(message_ids)

        print(f"✅ Archived {len(items)} emails")

        # Log actions
        if self.storage:
            for item in items:
                self.storage.log_action(
                    item.email.message_id, "archive",
                    category=item.decision.category
                )

        # Remove from review list
        for item in items:
            if item in self.items:
                self.items.remove(item)

        # Check for learning
        self._check_learning(items, "archive")

    async def _bulk_trello(self, indices: List[int]):
        """Create Trello cards for multiple emails."""
        items = [i for i in self.items if i.index in indices]

        print(f"\nCreating Trello cards for {len(items)} emails...")

        for item in items:
            try:
                card_info = await self.trello.create_card_from_email(
                    item.email,
                    self.account,
                    item.decision.category,
                    item.decision.priority,
                    item.decision.trello_suggestion
                )
                print(f"✅ [{item.index}] \"{item.decision.trello_suggestion.get('title', item.email.subject)[:50]}\"")

                # Archive email after creating card
                await self.gmail.archive(item.email.message_id)

                # Log action
                if self.storage:
                    board = item.decision.trello_suggestion.get('board', 'inbox') if item.decision.trello_suggestion else 'inbox'
                    self.storage.log_action(
                        item.email.message_id, "trello",
                        board=board,
                        trello_card_id=card_info.get("id") if card_info else None
                    )

            except Exception as e:
                print(f"❌ [{item.index}] Failed: {e}")

        # Remove from review list
        for item in items:
            if item in self.items:
                self.items.remove(item)

        print(f"\n✅ Created {len(items)} Trello cards and archived emails")

    async def _create_trello_card(self, item: ReviewItem):
        """Create Trello card for single email."""
        try:
            card_info = await self.trello.create_card_from_email(
                item.email,
                self.account,
                item.decision.category,
                item.decision.priority,
                item.decision.trello_suggestion
            )
            print(f"✅ Created Trello card: {card_info['url']}")

            # Archive email
            await self.gmail.archive(item.email.message_id)
            print("✅ Archived email")

            # Log action
            if self.storage:
                board = item.decision.trello_suggestion.get('board', 'inbox') if item.decision.trello_suggestion else 'inbox'
                self.storage.log_action(
                    item.email.message_id, "trello",
                    board=board,
                    trello_card_id=card_info.get("id")
                )

            # Remove from review list
            if item in self.items:
                self.items.remove(item)

        except Exception as e:
            print(f"❌ Failed to create Trello card: {e}")

    async def _archive_email(self, item: ReviewItem):
        """Archive single email."""
        try:
            await self.gmail.archive(item.email.message_id)
            print("✅ Archived email")

            if self.storage:
                self.storage.log_action(
                    item.email.message_id, "archive",
                    category=item.decision.category
                )

            if item in self.items:
                self.items.remove(item)
        except Exception as e:
            print(f"❌ Failed to archive: {e}")

    def _show_full_email(self, item: ReviewItem):
        """Show full email body."""
        print("\n" + "━" * 80)
        print("FULL EMAIL BODY")
        print("━" * 80)

        # Fetch full body if not cached
        if not item.email.body:
            item.email.body = self.gmail.get_email_body(item.email.message_id)

        print(item.email.body)
        print("━" * 80)

    def _check_learning(self, items: List[ReviewItem], action: str):
        """Check if user action patterns suggest a new rule."""
        # Group by domain
        domain_counts = defaultdict(int)

        for item in items:
            domain = item.email.from_addr.split('@')[-1]
            domain_counts[domain] += 1

        # Aggressive learning: suggest after 3 similar actions
        for domain, count in domain_counts.items():
            if count >= 3:
                print(f"\n💡 Learning opportunity:")
                print(f"You {action}d {count} emails from {domain}.")
                response = input(f"Auto-{action} emails from {domain} in the future? (yes/no/not now): ").strip().lower()

                if response == 'yes':
                    print(f"✅ Added learned rule: auto_{action}_{domain}")
                    # TODO: Implement rule learning

    def _filter_category(self, category: str):
        """Show only specific category."""
        if category == 'urgent':
            items = self.urgent
        elif category == 'important':
            items = self.important
        elif category == 'other':
            items = self.other
        else:
            print(f"❌ Unknown category: {category}")
            return

        print(f"\n{category.upper()} ({len(items)} emails):\n")
        for item in items:
            print(item.summary_line())
            print()

    def _finish_session(self):
        """Finish review session and show summary."""
        processed = len([i for i in self.original_items if i not in self.items])
        remaining = len(self.items)

        print("\n" + "━" * 80)
        print("✅ REVIEW SESSION COMPLETE")
        print("━" * 80)
        print(f"Processed: {processed} emails")
        print(f"Remaining: {remaining} emails")

        if remaining > 0:
            print(f"\n💡 Run the command again to process remaining {remaining} emails")
