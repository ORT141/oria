from __future__ import annotations
"""
ORIA Bot — Authentication Middleware

Checks every incoming message/callback against the Flask backend
to verify the Telegram user has a linked ORIA account.

S-01: Uses an in-memory TTL cache to reduce API calls per message.
"""

import time
import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update

from bot.config import WEB_APP_URL
from bot import api_client

logger = logging.getLogger(__name__)

# ── In-memory user cache with TTL (S-01) ────────────────────────────────────
_user_cache: dict[int, tuple[float, dict]] = {}
CACHE_TTL = 300  # 5 minutes


from typing import Optional

async def _check_user_cached(telegram_id: int) -> Optional[dict]:
    """Check user with caching to avoid an API call on every single message."""
    now = time.time()
    if telegram_id in _user_cache:
        ts, data = _user_cache[telegram_id]
        if now - ts < CACHE_TTL:
            return data

    result = await api_client.check_user(telegram_id)
    if "error" not in result:
        _user_cache[telegram_id] = (now, result)
        return result
    return None


def invalidate_cache(telegram_id: int) -> None:
    """Remove a user from the cache (call after linking/unlinking)."""
    _user_cache.pop(telegram_id, None)


class AuthMiddleware(BaseMiddleware):
    """
    If user is linked → inject oria_user into handler data.
    If not → reply with a link-account prompt and short-circuit.
    """

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        telegram_id = event.from_user.id if event.from_user else None
        if telegram_id is None:
            return  # System message — ignore

        # ─── Track every user ID in the global backend tracker (New) ────────
        await api_client.register_user(telegram_id)

        user_data = await _check_user_cached(telegram_id)

        if user_data:
            data["oria_user"] = user_data
            return await handler(event, data)

        # Allow /start command to bypass middleware for unlinked users
        if isinstance(event, Message) and event.text and event.text.startswith('/start'):
            # Pass None so the start handler knows the user isn't linked
            data["oria_user"] = None
            return await handler(event, data)

        # Not linked — send prompt
        link_url = f"{WEB_APP_URL}/login?tg_link={telegram_id}"
        text = (
            "🔒 <b>Account Not Linked</b>\n\n"
            "To use ORIA via Telegram, first link your account:\n"
            f'👉 <a href="{link_url}">Click here to link your ORIA account</a>\n\n'
            "After linking, send /start again."
        )
        if isinstance(event, Message):
            await event.answer(text, parse_mode="HTML", disable_web_page_preview=True)
        elif isinstance(event, CallbackQuery):
            await event.answer("Account not linked. Please use /start first.", show_alert=True)
        return None
