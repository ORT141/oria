"""
ORIA Bot — FSM States
Finite-state-machine groups used by the bot's conversational flows.
"""

from aiogram.fsm.state import StatesGroup, State


class CreateQuestFSM(StatesGroup):
    """Three-step wizard for creating a new quest via the AI."""
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_difficulty = State()


class AdminStates(StatesGroup):
    """Admin-only flows."""
    waiting_for_broadcast_target = State()
    waiting_for_broadcast_message = State()
