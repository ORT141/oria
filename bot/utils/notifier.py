"""
ORIA Bot — Proactive Notification API
Starts an internal aiohttp web server to listen for push notifications from the Flask backend.
"""

from __future__ import annotations

import logging
from aiohttp import web
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

logger = logging.getLogger(__name__)

async def notify_handler(request: web.Request) -> web.Response:
    """Handle incoming POST requests to send a notification."""
    bot: Bot = request.app["bot"]
    try:
        data = await request.json()
    except ValueError:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    telegram_id = data.get("telegram_id")
    message = data.get("message")

    if not telegram_id or not message:
        return web.json_response({"error": "Missing telegram_id or message"}, status=400)

    try:
        await bot.send_message(chat_id=telegram_id, text=message, parse_mode="HTML")
        logger.info(f"✅ Proactive notification sent to {telegram_id}: {message[:50]}...")
        return web.json_response({"status": "success"})
    except TelegramAPIError as e:
        logger.error(f"Failed to send notification to {telegram_id}: {e}")
        return web.json_response({"error": str(e)}, status=500)


def setup_notifier_app(bot: Bot) -> web.Application:
    """Create and configure the aiohttp application for notifications."""
    app = web.Application()
    app["bot"] = bot
    app.router.add_post("/api/notify", notify_handler)
    return app
