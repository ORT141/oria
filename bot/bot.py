"""
ORIA Telegram Bot — Entry Point
================================
Async bot for the ORIA productivity ecosystem (aiogram 3.x).
Designed to be launched from app.py in a background thread.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot import api_client
from bot.config import BOT_TOKEN, NOTIFIER_PORT
from bot.middleware import AuthMiddleware

from bot.handlers.start import router as start_router
from bot.handlers.admin import router as admin_router

logger = logging.getLogger("oria_bot")


# ── Lifecycle hooks ──────────────────────────────────────────────────────────

async def on_startup(bot: Bot) -> None:
    me = await bot.get_me()
    logger.info("🦝 ORIA Bot started — @%s (id=%s)", me.username, me.id)


async def on_shutdown(bot: Bot) -> None:
    logger.info("🛑 Shutting down ORIA Bot…")
    await api_client.close_session()


# ── Main async entry ─────────────────────────────────────────────────────────

async def _main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    dp.include_router(start_router)
    dp.include_router(admin_router)

    # Start the proactive notifier aiohttp server
    from bot.utils.notifier import setup_notifier_app
    from aiohttp import web

    app = setup_notifier_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', NOTIFIER_PORT)
    await site.start()
    logger.info("🌐 Proactive Notifier API listening on 0.0.0.0:%s", NOTIFIER_PORT)

    logger.info("🚀 Starting long-polling…")
    try:
        await dp.start_polling(bot, handle_signals=False)
    finally:
        await runner.cleanup()


def run_bot() -> None:
    """Run the bot in the current thread's event loop (blocking).
    Designed to be called from a daemon thread via threading.Thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    except Exception:
        logger.exception("Bot crashed")
    finally:
        loop.close()
