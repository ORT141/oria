import logging
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.config import ADMIN_IDS
from bot.states import AdminStates
from bot import api_client

router = Router(name="admin")
logger = logging.getLogger(__name__)


@router.message(F.text == "📢 Broadcast")
async def cmd_broadcast_start(message: Message, state: FSMContext) -> None:
    """Step 1: Ask the admin to choose the target audience."""
    if not message.from_user or message.from_user.id not in ADMIN_IDS:
        return  # Silently ignore non-admins

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 Все пользователи", callback_data="broadcast:all"),
            InlineKeyboardButton(text="🔗 Только привязанные", callback_data="broadcast:linked"),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast:cancel")]
    ])

    await message.answer(
        "🎯 <b>Выберите аудиторию для рассылки:</b>\n\n"
        "• <b>Все пользователи</b> — все, кто когда-либо запускал бота.\n"
        "• <b>Только привязанные</b> — только те, кто линковал аккаунт ORIA.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_broadcast_target)


@router.callback_query(AdminStates.waiting_for_broadcast_target)
async def cmd_broadcast_target_selected(callback: CallbackQuery, state: FSMContext) -> None:
    """Step 2: Audience selected, now ask for the message content."""
    if callback.data == "broadcast:cancel":
        await state.clear()
        await callback.message.edit_text("❌ Рассылка отменена.")
        return

    only_linked = (callback.data == "broadcast:linked")
    await state.update_data(only_linked=only_linked)

    target_text = "🔗 <b>Только привязанные</b>" if only_linked else "📢 <b>Все пользователи</b>"
    
    await callback.message.edit_text(
        f"Выбрана аудитория: {target_text}\n\n"
        "Введите текст сообщения для рассылки (поддерживается HTML):",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)


@router.message(AdminStates.waiting_for_broadcast_message)
async def cmd_broadcast_execute(message: Message, state: FSMContext, bot: Bot) -> None:
    """Step 3: Execute the broadcast based on the selection."""
    if not message.from_user or message.from_user.id not in ADMIN_IDS:
        await state.clear()
        return

    broadcast_text = message.text
    if not broadcast_text:
        await message.answer("❌ Ошибка: Сообщение не может быть пустым.")
        return

    data = await state.get_data()
    only_linked = data.get("only_linked", False)
    
    await state.clear()
    status_msg = await message.answer("🔄 Подготовка рассылки...")

    # 1. Fetch filtered Telegram IDs from Flask API
    result = await api_client.get_all_telegram_ids(only_linked=only_linked)
    if "error" in result:
        await message.answer(f"❌ Ошибка загрузки ID: {result['error']}")
        return

    user_ids = result.get("telegram_ids", [])
    if not user_ids:
        await status_msg.edit_text("⚠️ В выбранной категории нет пользователей.")
        return

    await status_msg.edit_text(f"🚀 Начинаю рассылку на {len(user_ids)} чел...")
    
    success_count = 0
    fail_count = 0

    # 2. Iterate and send
    for uid in user_ids:
        try:
            await bot.send_message(
                uid, 
                f"📢 <b>ORIA SYSTEM BROADCAST</b>\n\n{broadcast_text}", 
                parse_mode="HTML"
            )
            success_count += 1
            await asyncio.sleep(0.05) 
        except Exception as e:
            logger.error(f"Failed to send broadcast to {uid}: {e}")
            fail_count += 1

    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"Успешно: {success_count}\n"
        f"Ошибки: {fail_count}",
        parse_mode="HTML"
    )
