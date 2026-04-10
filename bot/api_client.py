from __future__ import annotations
"""
ORIA Bot — Async API Client

Communicates with the Flask backend over HTTP.
This module manages a shared aiohttp.ClientSession for efficiency.

Security fixes applied:
  - C-02: X-Bot-Api-Key header on every request
  - W-08: Handle asyncio.TimeoutError and non-JSON responses
"""

import asyncio
import logging
from typing import Any

import aiohttp

from bot.config import FLASK_API_BASE_URL, BOT_API_KEY

logger = logging.getLogger(__name__)

from typing import Optional
_session: Optional[aiohttp.ClientSession] = None


async def get_session() -> aiohttp.ClientSession:
    """Return (or create) a shared aiohttp session with the API key header."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            base_url=FLASK_API_BASE_URL,
            headers={"X-Bot-Api-Key": BOT_API_KEY},  # C-02
            timeout=aiohttp.ClientTimeout(total=60),
        )
    return _session


async def close_session() -> None:
    """Close the shared session (call on bot shutdown)."""
    global _session
    if _session and not _session.closed:
        await _session.close()
    _session = None


# ─── Low-level request helpers ──────────────────────────────────────────────

async def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST JSON to Flask backend. Returns parsed response or error dict."""
    session = await get_session()
    try:
        async with session.post(path, json=payload) as resp:
            # W-08: Safely parse the response body
            try:
                data = await resp.json()
            except (aiohttp.ContentTypeError, ValueError):
                text = await resp.text()
                logger.error("Non-JSON response from %s (HTTP %s): %s", path, resp.status, text[:200])
                return {"error": f"Server returned non-JSON response (HTTP {resp.status})"}

            if resp.status >= 400:
                logger.warning("API %s → HTTP %s  %s", path, resp.status, data)
            return data
    except asyncio.TimeoutError:
        logger.error("Timeout calling %s", path)
        return {"error": "Request timed out. The server may be overloaded."}
    except aiohttp.ClientError as exc:
        logger.error("API request to %s failed: %s", path, exc)
        return {"error": f"Connection error: {exc}"}


async def _get(path: str) -> dict[str, Any]:
    """GET from Flask backend. Returns parsed response or error dict."""
    session = await get_session()
    try:
        async with session.get(path) as resp:
            try:
                data = await resp.json()
            except (aiohttp.ContentTypeError, ValueError):
                text = await resp.text()
                logger.error("Non-JSON response from %s (HTTP %s): %s", path, resp.status, text[:200])
                return {"error": f"Server returned non-JSON response (HTTP {resp.status})"}

            if resp.status >= 400:
                logger.warning("API GET %s → HTTP %s  %s", path, resp.status, data)
            return data
    except asyncio.TimeoutError:
        logger.error("Timeout calling %s", path)
        return {"error": "Request timed out. The server may be overloaded."}
    except aiohttp.ClientError as exc:
        logger.error("API GET request to %s failed: %s", path, exc)
        return {"error": f"Connection error: {exc}"}


# ─── Public API functions ───────────────────────────────────────────────────

async def check_user(telegram_id: int) -> dict:
    """Check if a Telegram user has a linked ORIA account."""
    return await _post("/api/bot/check_user", {"telegram_id": telegram_id})


async def get_state(telegram_id: int) -> dict:
    """Fetch the full user state for a linked Telegram user."""
    return await _post("/api/bot/get_state", {"telegram_id": telegram_id})


async def send_chat(telegram_id: int, message: str) -> dict:
    """Send a chat message to the ORIA AI on behalf of a user."""
    return await _post("/api/bot/chat", {
        "telegram_id": telegram_id,
        "message": message,
    })


async def award_xp(telegram_id: int, amount: int) -> dict:
    """Award XP to a user."""
    return await _post("/api/bot/user/action", {
        "telegram_id": telegram_id,
        "type": "award_xp",
        "amount": amount,
    })


async def update_state(telegram_id: int, **fields) -> dict:
    """Update specific user state fields (quests, daily_quests, etc.)."""
    payload: dict[str, Any] = {"telegram_id": telegram_id}
    payload.update(fields)
    return await _post("/api/bot/user/update", payload)


async def complete_miniquest(telegram_id: int, global_index: int, mini_index: int) -> dict:
    """Mark a sub-task as completed."""
    return await _post("/api/bot/miniquest/complete", {
        "telegram_id": telegram_id,
        "global_index": global_index,
        "mini_index": mini_index,
    })


async def refresh_daily_quests(telegram_id: int) -> dict:
    """Request new daily quests from the backend."""
    return await _post("/api/bot/user/daily_refresh", {
        "telegram_id": telegram_id,
    })


async def claim_reward(telegram_id: int, level: int) -> dict:
    """Claim a level reward."""
    return await _post("/api/bot/rewards/claim", {
        "telegram_id": telegram_id,
        "level": level,
    })


async def generate_quiz(topic: str) -> dict:
    """Generate a quiz for the given topic."""
    return await _post("/api/bot/quiz/generate", {"topic": topic})


async def explain_quiz(question: str, user_answer: str, correct_answer: str) -> dict:
    """Get an AI explanation for a quiz answer."""
    return await _post("/api/bot/quiz/explain", {
        "question": question,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
    })


async def get_leaderboard() -> dict:
    """Fetch the leaderboard."""
    return await _get("/api/bot/leaderboard")


async def register_user(telegram_id: int) -> dict:
    """Register a Telegram ID in the backend's global tracker."""
    return await _post("/api/bot/register_user", {"telegram_id": telegram_id})


async def get_all_telegram_ids(only_linked: bool = False) -> dict:
    """Fetch Telegram IDs for broadcast (all or linked only)."""
    return await _get(f"/api/bot/telegram_ids?only_linked={str(only_linked).lower()}")

