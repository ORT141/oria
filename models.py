from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class User(db.Model):
    # ── Composite index for leaderboard query (W-11) ─────────────────────────
    __table_args__ = (
        db.Index('idx_user_level_xp', 'level', 'xp'),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    pronouns = db.Column(db.String(200)) # Stored as comma-separated string
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=0)
    chat_history = db.Column(db.Text, default='[]')
    quests = db.Column(db.Text, default='[]')
    owned_skins = db.Column(db.Text, default='["default"]')
    equipped_skin = db.Column(db.String(50), default='default')
    daily_quests = db.Column(db.Text, default='[]')
    last_daily_date = db.Column(db.String(20), default='')
    current_streak = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.String(20), default='')
    achievements = db.Column(db.Text, default='[]')
    onboarding_data = db.Column(db.Text, default='{}')
    claimed_rewards = db.Column(db.Text, default='[1]')
    equipped_title = db.Column(db.String(64), default='')
    telegram_id = db.Column(db.String(64), unique=True, nullable=True)
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    prefix = db.Column(db.String(100), nullable=True)  # Legacy, unused

    @property
    def is_admin(self):
        return self.role in ('admin', 'superadmin')

    @property
    def is_superadmin(self):
        return self.role == 'superadmin'

    def __init__(self, username, email, password, pronouns=""):
        self.username = username
        self.email = email
        self.password = password
        self.pronouns = pronouns
        self.level = 1
        self.xp = 0
        self.coins = 0
        self.chat_history = '[]'
        self.quests = '[]'
        self.owned_skins = '["default"]'
        self.equipped_skin = 'default'
        self.daily_quests = '[]'
        self.last_daily_date = ''
        self.current_streak = 0
        self.last_active_date = ''
        self.achievements = '[]'
        self.onboarding_data = '{}'
        self.claimed_rewards = '[1]'
        self.equipped_title = ''

    def get_chat_history(self):
        try:
            return json.loads(self.chat_history)
        except Exception:
            return []

    def set_chat_history(self, history_list):
        self.chat_history = json.dumps(history_list)

    def get_quests(self):
        try:
            return json.loads(self.quests)
        except Exception:
            return []

    def set_quests(self, quests_list):
        self.quests = json.dumps(quests_list)

    def get_daily_quests(self):
        try:
            return json.loads(self.daily_quests)
        except Exception:
            return []

    def set_daily_quests(self, daily_list):
        self.daily_quests = json.dumps(daily_list)

    def get_owned_skins(self):
        try:
            return json.loads(self.owned_skins)
        except Exception:
            return ["default"]

    def set_owned_skins(self, skins_list):
        self.owned_skins = json.dumps(skins_list)

    def get_achievements(self):
        try:
            return json.loads(self.achievements)
        except Exception:
            return []

    def set_achievements(self, achievements_list):
        self.achievements = json.dumps(achievements_list)

    def get_onboarding_data(self):
        try:
            return json.loads(self.onboarding_data or '{}')
        except Exception:
            return {}

    def set_onboarding_data(self, data_dict):
        self.onboarding_data = json.dumps(data_dict)

    def get_claimed_rewards(self):
        try:
            return json.loads(self.claimed_rewards or '[1]')
        except Exception:
            return [1]

    def set_claimed_rewards(self, rewards_list):
        self.claimed_rewards = json.dumps(rewards_list)

    def __repr__(self):
        return f'<User {self.username}>'


class TelegramUser(db.Model):
    """Tracks every Telegram ID that ever interacted with the bot, even if not linked."""
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<TelegramUser {self.telegram_id}>'


class ExclusiveTitle(db.Model):
    """Admin-managed exclusive titles that can be assigned to users."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    is_system = db.Column(db.Boolean, default=False)  # True = from LEVEL_REWARDS, cannot be deleted
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<ExclusiveTitle {self.name}>'


class AdminLog(db.Model):
    """Audit trail for all admin panel actions."""
    __table_args__ = (
        db.Index('idx_adminlog_created', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, nullable=False)       # Who performed the action
    admin_name = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(50), nullable=False)       # e.g. 'force_title', 'modify_coins'
    target_id = db.Column(db.Integer, nullable=True)        # Target user ID (if applicable)
    target_name = db.Column(db.String(80), nullable=True)
    old_value = db.Column(db.String(200), nullable=True)
    new_value = db.Column(db.String(200), nullable=True)
    details = db.Column(db.String(300), nullable=True)      # Free text for extra context
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<AdminLog {self.action} by {self.admin_name}>'

