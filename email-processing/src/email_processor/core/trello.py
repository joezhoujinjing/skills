"""Trello client with smart multi-board routing."""

import subprocess
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Tuple

from ..models.email import Email
from .secrets import resolve_secret


class TrelloRouter:
    """Simplified router - board ALWAYS chosen by LLM."""

    def __init__(self, trello_config: dict, default_board: str = "inbox"):
        self.boards = trello_config.get('boards', {})
        self.default_board = default_board

    def route_email(self, email: Email, account: str, category: str,
                   priority: int, llm_suggestion: Optional[dict] = None) -> Tuple[str, float, str]:
        """
        Determine which board to use.
        Board is ALWAYS chosen by LLM, with fallback to account default.

        Returns: (board_name, confidence, reason)
        """

        # 1. Use LLM suggestion (primary routing method)
        if llm_suggestion and llm_suggestion.get('board'):
            suggested_board = llm_suggestion.get('board')
            if suggested_board in self.boards:
                confidence = llm_suggestion.get('confidence', 0.8)
                return (suggested_board, confidence, f"LLM selected: {suggested_board}")

        # 2. Fallback to account default
        return (self.default_board, 0.5, f"Fallback to {self.default_board} (no LLM board suggestion)")


class TrelloClient:
    """Trello client with multi-board routing."""

    def __init__(self, trello_config: dict, default_board: str = "inbox"):
        self.config = trello_config
        self.router = TrelloRouter(trello_config, default_board)

        # Get credentials
        creds = trello_config.get('credentials', {})
        self.api_key = resolve_secret(creds.get('api_key', 'gsm:trello-api-key'))
        self.token = resolve_secret(creds.get('token', 'gsm:trello-token'))

        # Cache board and list IDs
        self._board_cache = {}
        self._list_cache = {}
        self._initialize_cache()

    def _initialize_cache(self):
        """Pre-fetch and cache board/list IDs."""
        try:
            # Fetch all boards
            result = subprocess.run(
                ["curl", "-s",
                 f"https://api.trello.com/1/members/me/boards?key={self.api_key}&token={self.token}"],
                capture_output=True, text=True, check=True
            )
            boards = json.loads(result.stdout)

            # Map board names to IDs
            board_name_to_id = {b['name'].lower(): b['id'] for b in boards}

            # Cache each configured board
            for board_key, board_config in self.router.boards.items():
                board_id = board_config.get('id')
                if board_id == 'auto':
                    # Look up by name
                    board_id = board_name_to_id.get(board_key.lower())

                if not board_id:
                    print(f"⚠️  Warning: Board '{board_key}' not found")
                    continue

                self._board_cache[board_key] = board_id

                # Fetch lists for this board
                result = subprocess.run(
                    ["curl", "-s",
                     f"https://api.trello.com/1/boards/{board_id}/lists?key={self.api_key}&token={self.token}"],
                    capture_output=True, text=True, check=True
                )
                lists = json.loads(result.stdout)

                # Cache list IDs
                for lst in lists:
                    cache_key = f"{board_key}:{lst['name'].lower()}"
                    self._list_cache[cache_key] = lst['id']

        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize Trello cache: {e}")

    async def create_card_from_email(self, email: Email, account: str,
                                    category: str, priority: int,
                                    suggestion: Optional[dict] = None) -> dict:
        """
        Create Trello card with smart routing.

        Returns: {
            'url': card_url,
            'board': board_name,
            'list': list_name,
            'confidence': routing_confidence,
            'reason': routing_reason
        }
        """

        # Route to correct board
        board_key, confidence, reason = self.router.route_email(
            email, account, category, priority, suggestion
        )

        # Get board and list
        board_id = self._board_cache.get(board_key)
        if not board_id:
            # Fallback to inbox
            board_key = 'inbox'
            board_id = self._board_cache.get(board_key)
            reason = f"Fallback to inbox (original board not found)"

        # Determine list based on priority
        board_config = self.router.boards[board_key]
        if priority == 0:
            list_name = board_config['lists']['urgent']
        else:
            list_name = board_config['lists']['normal']

        list_cache_key = f"{board_key}:{list_name.lower()}"
        list_id = self._list_cache.get(list_cache_key)

        if not list_id:
            raise Exception(f"List '{list_name}' not found in board '{board_key}'")

        # Prepare card data
        if suggestion:
            title = suggestion.get('title', email.subject[:60])
            action = suggestion.get('action', 'Review and take appropriate action')
            due_days = suggestion.get('due_days', 1)
        else:
            title = email.subject[:60]
            action = 'Review and take appropriate action'
            due_days = 1 if priority == 0 else 3

        # Calculate due date
        due_date = datetime.now() + timedelta(days=due_days)
        due_date_str = due_date.strftime("%Y-%m-%dT23:59:59.000Z")

        # Format description
        description = self._format_card_description(email, action, account,
                                                    board_key, confidence, reason)

        # Create card
        card = await self._create_card_api(
            list_id=list_id,
            name=title,
            desc=description,
            due=due_date_str
        )

        # Display routing info
        print(f"   ✅ Created in {board_key}/{list_name}: {title[:50]}")
        if confidence < 0.8:
            print(f"      ℹ️  Routing: {reason} (confidence: {confidence:.0%})")

        return {
            'url': card['shortUrl'],
            'board': board_key,
            'list': list_name,
            'confidence': confidence,
            'reason': reason
        }

    def _format_card_description(self, email: Email, action: str, account: str,
                                board: str, confidence: float, reason: str) -> str:
        """Format card description."""
        gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{email.message_id}"

        return f"""## Email Context
- **From**: {email.from_addr}
- **To**: {email.to_addr}
- **Date**: {email.date.strftime('%Y-%m-%d %I:%M %p')}
- **Subject**: {email.subject}
- **Account**: {account.upper()}

## Original Message
{email.snippet}

[📧 View full email in Gmail]({gmail_link})

## Next Action
{action}

## Routing Info
- **Board**: {board}
- **Confidence**: {confidence:.0%}
- **Reason**: {reason}

---
_Created from email: {email.message_id}_
_Created: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}_"""

    async def _create_card_api(self, list_id: str, name: str, desc: str, due: str) -> dict:
        """Create card via API."""
        cmd = [
            "curl", "-s", "-X", "POST",
            f"https://api.trello.com/1/cards?key={self.api_key}&token={self.token}",
            "-d", f"idList={list_id}",
            "-d", f"name={name}",
            "-d", f"desc={desc}",
            "-d", f"due={due}",
            "-d", "pos=top"
        ]

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(cmd, capture_output=True, text=True, check=True)
        )

        return json.loads(result.stdout)
