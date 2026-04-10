"""
ORIA Bot — Keyboards
All ReplyKeyboardMarkup and InlineKeyboardMarkup definitions live here.
"""

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)

from bot.config import WEB_APP_URL, ADMIN_IDS


# ──────────────────────────────────────────────────────────────────────────────
# Main Menu (dynamic reply keyboard)
# ──────────────────────────────────────────────────────────────────────────────

def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    """Return a reply keyboard. If user is an admin, include '📢 Broadcast'."""
    buttons = [
        [
            KeyboardButton(text="⚙️ Settings"),
            KeyboardButton(text="❓ Help"),
        ]
    ]

    # Add the admin button if the user's ID is in the global ADMIN_IDS list
    if user_id in ADMIN_IDS:
        buttons.append([KeyboardButton(text="📢 Broadcast")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Select an option...",
    )

# ──────────────────────────────────────────────────────────────────────────────
# Inline: WebApp Dashboard
# ──────────────────────────────────────────────────────────────────────────────

def get_dashboard_keyboard(web_url: str) -> InlineKeyboardMarkup:
    """Return an inline keyboard for launching the WebApp Dashboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Open ORIA Dashboard", 
                web_app=WebAppInfo(url=web_url)
            )
        ]
    ])


# ──────────────────────────────────────────────────────────────────────────────
# Inline: Link account button
# ──────────────────────────────────────────────────────────────────────────────

def link_account_keyboard(web_url: str, telegram_id: int) -> InlineKeyboardMarkup:
    """Return an inline keyboard with a deep-link to the web app for linking."""
    url = f"{web_url}/link-telegram?tg_id={telegram_id}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Link ORIA Account", url=url)]
    ])
