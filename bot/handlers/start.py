"""
ORIA Bot — /start and account-linking handler
"""

from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove

from bot.config import WEB_APP_URL
from bot.keyboards import get_main_menu, link_account_keyboard, get_dashboard_keyboard

router = Router(name="start")
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message, oria_user: dict | None) -> None:
    """Handle /start — check linking status and either greet or prompt linking."""
    if not message.from_user:
        return

    tg_id = message.from_user.id
    
    # ──────────────────────────────────────────────────────────────────────────
    # CASE A: User is already linked to ORIA
    # ──────────────────────────────────────────────────────────────────────────
    if oria_user:
        username = oria_user.get("username", "Operative")
        level = oria_user.get("level", 1)
        xp = oria_user.get("xp", 0)
        coins = oria_user.get("coins", 0)
        
        # Message 1 (Natural Greeting & UI Sync)
        # We attach the minimalist main_menu ReplyKeyboard here to clear old "zombie" keyboards.
        await message.answer(
            f"👋 Welcome back, {username}! Fetching your profile...",
            reply_markup=get_main_menu(tg_id)
        )

        # Message 2 (The Payload)
        # We attach the Inline WebApp button here.
        # NOTE: Telegram REQUIRES an HTTPS URL for WebAppInfo. 
        # If WEB_APP_URL is http://, it will crash.
        keyboard_url = WEB_APP_URL
        if not keyboard_url.startswith("https://"):
            logger.warning(f"⚠️ WEB_APP_URL is not HTTPS ({WEB_APP_URL}); converting to HTTPS to prevent crash.")
            keyboard_url = keyboard_url.replace("http://", "https://")

        await message.answer(
            f"📊 Level: {level} | XP: {xp} | Coins: {coins}\n\n"
            f"🤖 ORIA is online and listening. Keep pushing your limits!",
            reply_markup=get_dashboard_keyboard(keyboard_url)
        )

    # ──────────────────────────────────────────────────────────────────────────
    # CASE B: User is NOT linked (Onboarding Flow)
    # ──────────────────────────────────────────────────────────────────────────
    else:
        # Message 1: The Onboarding instructions + Inline link button
        await message.answer(
            "🔒 <b>Account Authentication Required</b>\n\n"
            "Welcome to the ORIA Ecosystem! To secure your progress and unlock the bot's features, "
            "you need to link your Telegram account to your ORIA profile.\n\n"
            "Tap the button below to open the secure Gateway and link up:",
            reply_markup=link_account_keyboard(WEB_APP_URL, tg_id),
            parse_mode="HTML",
        )
        
        # Message 2: Cleanup. We remove any old ReplyKeyboard (if any) for unlinked users.
        await message.answer(
            "<i>Note: Once linked, you'll gain access to the dashboard and settings.</i>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML"
        )


# ──────────────────────────────────────────────────────────────────────────────
# Reply Keyboard Button Handlers
# ──────────────────────────────────────────────────────────────────────────────

@router.message(F.text == "⚙️ Settings")
async def cmd_settings(message: Message) -> None:
    """Handle the '⚙️ Settings' reply button."""
    await message.answer("⚙️ Settings menu is under construction.")


@router.message(F.text == "❓ Help")
async def cmd_help(message: Message) -> None:
    """Handle the '❓ Help' reply button."""
    await message.answer("❓ Need help? Contact support.")
