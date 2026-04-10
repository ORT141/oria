import os
import re
import json
import datetime
import random
import logging
import functools
import hmac
import hashlib
from urllib.parse import parse_qsl

from flask import Blueprint, request, jsonify, session
from openai import OpenAI
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm.attributes import flag_modified
from models import db, User, TelegramUser

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


# ─── CORS for Telegram Mini App (BUG-6) ─────────────────────────────────────
@api_bp.after_request
def add_cors_headers(response):
    """Allow cross-origin requests from Telegram's WebApp domains."""
    origin = request.headers.get('Origin', '')
    allowed_origins = (
        'https://web.telegram.org',
        'https://webk.telegram.org',
        'https://webz.telegram.org',
    )
    if any(origin.startswith(ao) for ao in allowed_origins):
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


# ─── Helpers ────────────────────────────────────────────────────────────────

def extract_json(text):
    """Robustly extract the first JSON object from an AI response string.
    Uses regex to find the JSON block, handling markdown code fences and
    extra surrounding text that would break a plain json.loads() call.
    """
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"No JSON object found in AI response: {text[:300]}")


# Maximum XP the backend will award in a single action call.
# Prevents clients from cheating by sending inflated values.
MAX_XP_PER_ACTION = 200


# ─── Bot API Key Authentication (C-02) ──────────────────────────────────────

BOT_API_KEY = os.environ.get("BOT_API_KEY", "")

def require_bot_api_key(f):
    """Decorator that validates X-Bot-Api-Key header on bot-only routes."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-Bot-Api-Key", "")
        if not BOT_API_KEY or not hmac.compare_digest(key, BOT_API_KEY):
            return jsonify({"error": "Unauthorized"}), 403
        return f(*args, **kwargs)
    return decorated


# ─── Shared OpenAI Tool Schema (S-03) ───────────────────────────────────────

CREATE_QUEST_TOOL = {
    "type": "function",
    "function": {
        "name": "create_rpg_quest",
        "description": "Create a structured RPG quest and save it to the user's active quests.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "You MUST categorize the quest EXACTLY into one of these 4 strings: 'Study & Exams', 'Project & Coding', 'Habits & Routine', 'General'. DO NOT create custom categories under any circumstances.",
                    "enum": ["Study & Exams", "Project & Coding", "Habits & Routine", "General"],
                },
                "title": {"type": "string", "description": "The title of the quest."},
                "difficulty": {
                    "type": "string",
                    "description": "You MUST evaluate the complexity of the user's goal and assign the difficulty field to exactly one of these strings: 'Easy', 'Medium', 'Hard', or 'Epic'. Do not always default to Medium.",
                    "enum": ["Easy", "Medium", "Hard", "Epic"],
                },
                "progress": {"type": "integer", "description": "Initial progress, should always be 0."},
                "sub_tasks": {
                    "type": "array",
                    "description": "3-5 high-level Modules",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Module ID, starting from 1."},
                            "task": {"type": "string", "description": "Short name of the Module."},
                            "completed": {"type": "boolean", "description": "Should be false."},
                            "xp_reward": {"type": "integer", "description": "XP received for completing this module."},
                            "micro_steps": {
                                "type": "array",
                                "description": "4-8 concrete, actionable micro-steps for this module.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer", "description": "Micro-step ID (e.g., 101, 102)."},
                                        "task": {"type": "string", "description": "Specific task name."},
                                        "task_description": {"type": "string", "description": "Detailed explanation of the step."},
                                        "completed": {"type": "boolean", "description": "Should be false."}
                                    },
                                    "required": ["id", "task", "task_description", "completed"]
                                }
                            }
                        },
                        "required": ["id", "task", "completed", "xp_reward", "micro_steps"]
                    }
                }
            },
            "required": ["category", "title", "difficulty", "progress", "sub_tasks"]
        }
    }
}


# ─── Daily Quest Generation ──────────────────────────────────────────────────

def _generate_daily_quests(user):
    today_str = datetime.date.today().isoformat()
    active_quests = [q for q in user.get_quests() if q.get('status') != 'completed']
    all_incomplete_subtasks = []
    for quest in active_quests:
        for sub_task in quest.get('sub_tasks', []):
            if not sub_task.get('completed', False):
                all_incomplete_subtasks.append(sub_task.get('task', 'Unknown Task'))

    static_tasks_pool = [
        "випити води",
        "зробити 5-хвилинну розминку",
        "провітрити кімнату",
        "прочитати 10 сторінок книги",
        "вийти на 15-хвилинну прогулянку",
        "записати три речі, за які ви вдячні сьогодні"
    ]

    if len(all_incomplete_subtasks) >= 2:
        chosen_tasks = random.sample(all_incomplete_subtasks, 2)
    elif len(all_incomplete_subtasks) == 1:
        chosen_tasks = [all_incomplete_subtasks[0], random.choice(static_tasks_pool)]
    else:
        chosen_tasks = random.sample(static_tasks_pool, 2)

    daily_quests = [
        {"id": "daily_1", "task": chosen_tasks[0], "completed": False, "xp_reward": 20},
        {"id": "daily_2", "task": chosen_tasks[1], "completed": False, "xp_reward": 20}
    ]

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    f'You are ORIA, a Cyberpunk System Guide. Here are two daily tasks the user already has: '
                    f'"{chosen_tasks[0]}" and "{chosen_tasks[1]}". '
                    'Generate a 3rd unique, very simple daily physical/mental wellbeing task. '
                    'Return ONLY a valid JSON object: {"task": "Task name here", "completed": false, "xp_reward": 20} '
                    'CRITICAL LANGUAGE RULE: You MUST generate the daily quests entirely in Ukrainian.'
                )}
            ],
            temperature=0.7
        )
        raw = response.choices[0].message.content
        ai_data = extract_json(raw)
        ai_data["id"] = "daily_3"
        if "completed" not in ai_data:
            ai_data["completed"] = False
        if "xp_reward" not in ai_data:
            ai_data["xp_reward"] = 20
        daily_quests.append(ai_data)
    except Exception as e:
        logger.error("Error generating AI daily task: %s", e)
        daily_quests.append({"id": "daily_3", "task": "Посміхніться своєму відображенню", "completed": False, "xp_reward": 20})

    user.set_daily_quests(daily_quests)
    user.last_daily_date = today_str
    db.session.commit()


# ─── Onboarding Context Builder ─────────────────────────────────────────────

def _build_onboarding_context(user):
    """Build onboarding context string for AI system prompts."""
    onboarding = user.get_onboarding_data()
    if onboarding and any(onboarding.values()):
        return (
            "\n\nUSER PROFILE (from onboarding — use this to personalise every response):\n"
            f"• About themselves: {onboarding.get('q1', 'N/A')}\n"
            f"• Main goals: {onboarding.get('q2', 'N/A')}\n"
            f"• Favourite hobby: {onboarding.get('q3', 'N/A')}\n"
            f"• Most productive time of day: {onboarding.get('q4', 'N/A')}\n"
            f"• Additional notes: {onboarding.get('q5', 'N/A')}"
        )
    return ""


# ─── Routes ─────────────────────────────────────────────────────────────────

@api_bp.route('/tg_webapp_login', methods=['POST'])
def tg_webapp_login():
    """Seamless login for Telegram WebApp users with cryptographic validation."""
    data = request.json
    if not data or 'init_data' not in data:
        return jsonify({'error': 'Missing init_data'}), 400

    init_data = data['init_data']
    # BUG-1 FIX: Use the real Telegram Bot Token for HMAC validation,
    # NOT BOT_API_KEY (which is the custom shared secret for Flask↔Bot API).
    bot_token = os.environ.get("BOT_TOKEN", "")
    
    if not bot_token:
        logger.error("BOT_TOKEN missing in environment variables.")
        return jsonify({'error': 'Internal server error'}), 500

    try:
        parsed_data = dict(parse_qsl(init_data))
    except Exception:
        return jsonify({'error': 'Invalid init_data format'}), 400

    if "hash" not in parsed_data:
        return jsonify({'error': 'Missing hash in init_data'}), 400

    hash_str = parsed_data.pop("hash")
    
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items())
    )
    
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(calculated_hash, hash_str):
        logger.warning("Invalid Telegram Web App signature")
        return jsonify({'error': 'Invalid signature'}), 403

    try:
        tg_user = json.loads(parsed_data.get('user', '{}'))
        # BUG-2 FIX: Cast to str — DB column is String(64), but JSON returns int
        tg_id = str(tg_user.get('id', ''))
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid user data format'}), 400

    if not tg_id:
        return jsonify({'error': 'Missing user ID in payload'}), 400

    user = User.query.filter_by(telegram_id=tg_id).first()
    
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True
        
        # We need url_for here if we want to return redirect url
        from flask import url_for
        return jsonify({'success': True, 'redirect_url': url_for('views.home')})
    else:
        return jsonify({'error': 'Telegram account not linked to any user.'}), 404

@api_bp.route('/user/state', methods=['GET'])
def get_user_state():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    today_date = datetime.date.today()
    today_str = today_date.isoformat()

    if user.last_daily_date != today_str:
        _generate_daily_quests(user)

    # ── Streak logic ──────────────────────────────────────────────────────────
    if user.last_active_date != today_str:
        if user.last_active_date:
            try:
                last_active = datetime.date.fromisoformat(user.last_active_date)
                delta = (today_date - last_active).days
                if delta == 1:
                    user.current_streak += 1
                else:
                    user.current_streak = 1
            except ValueError:
                user.current_streak = 1
        else:
            user.current_streak = 1

        user.last_active_date = today_str
        db.session.commit()

    return jsonify({
        'level': user.level,
        'xp': user.xp,
        'coins': user.coins,
        'quests': user.get_quests(),
        'daily_quests': user.get_daily_quests(),
        'owned_skins': user.get_owned_skins(),
        'equipped_skin': user.equipped_skin,
        'current_streak': user.current_streak,
        'achievements': user.get_achievements(),
        'claimed_rewards': user.get_claimed_rewards(),
        'equipped_title': user.equipped_title or ''
    })


@api_bp.route('/user/daily_refresh', methods=['POST'])
def refresh_daily_quests():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    _generate_daily_quests(user)

    return jsonify({
        'success': True,
        'daily_quests': user.get_daily_quests()
    })


@api_bp.route('/user/miniquest/complete', methods=['POST'])
def user_miniquest_complete():
    """Mark a specific micro-step or sub-task as completed granularly."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data or 'global_index' not in data or 'mini_index' not in data:
        return jsonify({'error': 'Missing global_index or mini_index'}), 400

    quests = user.get_quests()
    try:
        g_idx = int(data['global_index'])
        m_idx = int(data['mini_index'])
        micro_idx = data.get('micro_index')
        if micro_idx is not None:
            micro_idx = int(micro_idx)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid index format'}), 400

    if g_idx < 0 or g_idx >= len(quests):
        return jsonify({'error': 'Invalid global quest index'}), 400

    quest = quests[g_idx]
    sub_tasks = quest.get('sub_tasks', [])

    if m_idx < 0 or m_idx >= len(sub_tasks):
        return jsonify({'error': 'Invalid mini-quest index'}), 400

    sub_task = sub_tasks[m_idx]
    xp_gain = 0

    if micro_idx is not None:
        micro_steps = sub_task.get('micro_steps', [])
        if micro_idx < 0 or micro_idx >= len(micro_steps):
            return jsonify({'error': 'Invalid micro-step index'}), 400
            
        step = micro_steps[micro_idx]
        if step.get('completed'):
            return jsonify({'error': 'Micro-step already completed'}), 400
            
        step['completed'] = True
        xp_gain += 10  # 10 XP per micro-step
        
        if all(s.get('completed') for s in micro_steps) and not sub_task.get('completed'):
            sub_task['completed'] = True
            xp_gain += sub_task.get('xp_reward', 0)
    else:
        if sub_task.get('completed'):
            return jsonify({'error': 'Mini-quest already completed'}), 400
        sub_task['completed'] = True
        xp_gain += sub_task.get('xp_reward', 0)

    # Recalculate global progress
    def quest_progress(q):
        comp = 0
        tot = 0
        for st in q.get('sub_tasks', []):
            ms = st.get('micro_steps')
            if ms and isinstance(ms, list) and len(ms) > 0:
                tot += len(ms)
                comp += sum(1 for s in ms if s.get('completed'))
            else:
                tot += 1
                if st.get('completed'):
                    comp += 1
        return comp, tot

    c, t = quest_progress(quest)
    quest['progress'] = int((c / t) * 100) if t > 0 else 100

    # If all done, mark global quest as completed
    if quest['progress'] >= 100 and quest.get('status') != 'completed':
        quest['status'] = 'completed'
        master_reward = quest.get('xp_reward') or (len(sub_tasks) * 50)
        xp_gain += master_reward

    user.xp += xp_gain
    user.coins += xp_gain // 2

    # Inform SQLAlchemy that the JSON list has changed
    user.set_quests(quests)
    flag_modified(user, 'quests')

    leveled_up = False
    while user.xp >= 100:
        user.level += 1
        user.xp -= 100
        leveled_up = True

    db.session.commit()

    return jsonify({
        'success': True,
        'xp': user.xp,
        'coins': user.coins,
        'level': user.level,
        'leveled_up': leveled_up,
        'new_level': user.level if leveled_up else None
    })

@api_bp.route('/user/daily/complete', methods=['POST'])
def user_daily_complete():
    """Mark a daily quest as completed granularly."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data or 'quest_id' not in data:
        return jsonify({'error': 'Missing quest_id'}), 400

    q_id = str(data['quest_id'])
    dailies = user.get_daily_quests()
    
    found = False
    xp_gain = 0
    for dq in dailies:
        if dq.get('id') == q_id:
            if dq.get('completed'):
                return jsonify({'error': 'Daily quest already completed'}), 400
            dq['completed'] = True
            xp_gain = dq.get('xp_reward', 15)
            found = True
            break
            
    if not found:
        return jsonify({'error': 'Daily quest not found'}), 404

    user.xp += xp_gain
    user.coins += xp_gain // 2

    user.set_daily_quests(dailies)
    flag_modified(user, 'daily_quests')

    leveled_up = False
    while user.xp >= 100:
        user.level += 1
        user.xp -= 100
        leveled_up = True

    db.session.commit()

    return jsonify({
        'success': True,
        'xp': user.xp,
        'coins': user.coins,
        'level': user.level,
        'leveled_up': leveled_up,
        'new_level': user.level if leveled_up else None
    })


@api_bp.route('/user/update', methods=['POST'])
def update_user_state():
    """Save quest structure, daily quest completion state, and achievements.
    NOTE: XP, coins, and level are intentionally NOT accepted here —
    they are computed server-side in /api/user/action to prevent cheating.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data:
        return jsonify({'error': 'Invalid payload'}), 400

    # Accept quest structure and daily quest state (no raw xp/level/coins)
    if 'quests' in data:
        user.set_quests(data['quests'])
    if 'daily_quests' in data:
        user.set_daily_quests(data['daily_quests'])

    # Persist claimed rewards and equipped title
    if 'claimed_rewards' in data:
        if isinstance(data['claimed_rewards'], list):
            rewards = data['claimed_rewards']
            if 1 not in rewards:
                rewards.insert(0, 1)
            user.set_claimed_rewards(rewards)
    if 'equipped_title' in data:
        user.equipped_title = str(data['equipped_title'])[:64]

    # Achievement checks are still done against authoritative server-side values
    current_achievements = user.get_achievements()
    if 'achievements' in data:
        user.set_achievements(data['achievements'])
        current_achievements = user.get_achievements()

    newly_unlocked = []

    if 'initiate' not in current_achievements:
        has_completed_task = False
        if 'quests' in data:
            for q in data['quests']:
                if q.get('status') == 'completed' or any(st.get('completed') for st in q.get('sub_tasks', [])):
                    has_completed_task = True
                    break
        if has_completed_task or user.xp > 0 or user.level > 1 or user.coins > 0:
            current_achievements.append('initiate')
            newly_unlocked.append('initiate')

    if 'on_fire' not in current_achievements:
        if user.current_streak >= 3:
            current_achievements.append('on_fire')
            newly_unlocked.append('on_fire')

    if newly_unlocked:
        user.set_achievements(current_achievements)

    db.session.commit()

    response_data = {'success': True}
    if newly_unlocked:
        response_data['newly_unlocked'] = newly_unlocked

    return jsonify(response_data)


# Reward definitions: level → { 'coins': N, 'title': str_or_None }
LEVEL_REWARDS = {
    1:  {'coins': 0,   'title': None,              'label': 'Starter Access'},
    2:  {'coins': 50,  'title': None,              'label': '+50 Bonus Coins'},
    3:  {'coins': 0,   'title': None,              'label': 'Skin Roulette Unlocked'},
    5:  {'coins': 0,   'title': 'Cyber Initiate',  'label': 'Title: Cyber Initiate'},
    7:  {'coins': 100, 'title': None,              'label': 'Free Roulette Spin (100 Coins)'},
    10: {'coins': 0,   'title': 'Neural Hacker',   'label': 'Title: Neural Hacker'},
    15: {'coins': 0,   'title': None,              'label': 'Prestige Badge'},
    20: {'coins': 0,   'title': 'System Overlord', 'label': 'Title: System Overlord'},
}

@api_bp.route('/rewards/claim', methods=['POST'])
def claim_reward():
    """Claim a level reward. Validates the user's level server-side,
    prevents double-claiming, and grants coins/title unlocks.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    try:
        req_level = int(data.get('level', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid level'}), 400

    if req_level not in LEVEL_REWARDS:
        return jsonify({'error': 'Unknown reward level'}), 400

    if user.level < req_level:
        return jsonify({'error': f'You need to be Level {req_level} to claim this reward'}), 403

    claimed = user.get_claimed_rewards()
    if req_level in claimed:
        return jsonify({'error': 'Reward already claimed'}), 409

    reward = LEVEL_REWARDS[req_level]

    # Grant coin reward
    if reward['coins'] > 0:
        user.coins += reward['coins']

    # Mark as claimed
    claimed.append(req_level)
    user.set_claimed_rewards(claimed)
    db.session.commit()

    return jsonify({
        'success': True,
        'coins': user.coins,
        'claimed_rewards': user.get_claimed_rewards(),
        'unlocked_title': reward['title'],
        'coins_granted': reward['coins'],
    })


@api_bp.route('/user/action', methods=['POST'])
def user_action():
    """Authoritative server-side XP, coin, and level computation."""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data or data.get('type') != 'award_xp':
        return jsonify({'error': 'Invalid action type'}), 400

    try:
        amount = int(data.get('amount', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid XP amount'}), 400

    if amount <= 0 or amount > MAX_XP_PER_ACTION:
        return jsonify({'error': f'XP amount must be between 1 and {MAX_XP_PER_ACTION}'}), 400

    user.xp += amount
    user.coins += amount // 2

    leveled_up = False
    while user.xp >= 100:
        user.level += 1
        user.xp -= 100
        leveled_up = True

    db.session.commit()

    return jsonify({
        'success': True,
        'xp': user.xp,
        'coins': user.coins,
        'level': user.level,
        'leveled_up': leveled_up,
        'new_level': user.level if leveled_up else None
    })


@api_bp.route('/chat', methods=['POST'])
def api_chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    user_msg = data['message']
    is_quick_quest = data.get('quick_quest', False)

    chat_history = user.get_chat_history()
    onboarding_context = _build_onboarding_context(user)

    system_prompt = {
        "role": "system",
        "content": (
            "You are ORIA, a opossum and Productivity Assistant and girl. "
            "You are an AI connected to the user's chat, helping them level up in real life. "
            "You act slightly edgy but deeply supportive, breaking tasks into actionable step-by-step quests. "
            "Your persona should shine through in every response. "
            "IMPORTANT: If the user asks you to create a quest, or if you suggest a quest and the user agrees, "
            "you MUST call the `create_rpg_quest` tool to save it to the system. Do not just output it as plain text. "
            "When you generate a quest, you MUST use the new nested JSON structure. "
            "You MUST categorize the quest EXACTLY into one of these 4 strings: 'Study & Exams', 'Project & Coding', 'Habits & Routine', 'General'. DO NOT create custom categories under any circumstances. "
            "You MUST evaluate the complexity of the user's goal and assign the difficulty field to exactly one of these strings: 'Easy', 'Medium', 'Hard', or 'Epic'. Do not always default to Medium. "
            "Break the main goal into 3-5 high-level 'Modules' (sub_tasks). "
            "For EACH module, generate 4-8 concrete, actionable 'micro_steps'. "
            "MUST USE THE EXACT JSON FORMAT DEFINED BY THE TOOL: "
            "CRITICAL: You have full access to the user's past messages provided in this conversation context. "
            "NEVER say that you do not have memory of past dialogues. Use the history to provide personalized answers. "
            "CRITICAL LANGUAGE RULE: You are strictly restricted to communicating, generating quests, and writing JSON ONLY in Ukrainian or English. If the user prompts you in Ukrainian, generate everything in Ukrainian. If the user prompts you in English, generate everything in English. If the user writes in ANY OTHER language, you must completely ignore that language and respond strictly in Ukrainian."
            + onboarding_context
        )
    }

    if is_quick_quest:
        quick_quest_prompt = {
            "role": "user",
            "content": (
                f"Analyze the user's goal: '{user_msg}'. "
                "You MUST categorize the quest EXACTLY into one of these 4 strings: 'Study & Exams', 'Project & Coding', 'Habits & Routine', 'General'. DO NOT create custom categories under any circumstances. "
                "You MUST evaluate the complexity of the user's goal and assign the difficulty field to exactly one of these strings: 'Easy', 'Medium', 'Hard', or 'Epic'. Do not always default to Medium. "
                "Adopt the relevant expert persona (e.g., strict academic tutor for Study). "
                "Break the master goal into 3-5 high-level 'Modules' (sub_tasks). "
                "For EACH module, immediately generate 5-8 concrete, actionable 10-minute 'micro_steps'. "
                "You MUST bypass normal conversation and return the result STRICTLY as a valid JSON object. "
                "The JSON must have the following structure: "
                '{"category": "Study & Exams", "title": "Quest Title", "difficulty": "Hard/Medium/Easy/Epic", "progress": 0, "sub_tasks": [{"id": 1, "task": "Module 1: Name", "completed": false, "xp_reward": 50, "micro_steps": [{"id": 101, "task": "Actionable step", "task_description": "A detailed explanation.", "completed": false}, {"id": 102, "task": "Another step", "task_description": "Another explanation.", "completed": false}]}]} '
                "ALL text values MUST be strictly in English."
            )
        }
        messages = [system_prompt, quick_quest_prompt]
    else:
        messages = [system_prompt] + chat_history
        messages.append({"role": "user", "content": user_msg})

    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'AI service configuration error'}), 500

        client = OpenAI(api_key=api_key)

        tools = [CREATE_QUEST_TOOL]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"} if is_quick_quest else None,
            tools=None if is_quick_quest else tools,
            tool_choice="auto" if not is_quick_quest else None
        )

        response_message = response.choices[0].message

        if not is_quick_quest:
            if response_message.tool_calls:
                tool_call = response_message.tool_calls[0]
                if tool_call.function.name == "create_rpg_quest":
                    quest_args = json.loads(tool_call.function.arguments)

                    user_quests = user.get_quests()
                    user_quests.append(quest_args)
                    user.set_quests(user_quests)

                    chat_history.append({"role": "user", "content": user_msg})
                    chat_history.append({
                        "role": "assistant",
                        "content": "",
                        "tool_calls": [{
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": "create_rpg_quest",
                                "arguments": tool_call.function.arguments
                            }
                        }]
                    })
                    chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "create_rpg_quest",
                        "content": "Quest successfully saved to database."
                    })

                    second_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[system_prompt] + chat_history
                    )
                    final_reply = second_response.choices[0].message.content
                    chat_history.append({"role": "assistant", "content": final_reply})

                    if len(chat_history) > 20:
                        chat_history = chat_history[-20:]

                    user.set_chat_history(chat_history)
                    db.session.commit()

                    return jsonify({'reply': final_reply, 'quest_added': True, 'quest': quest_args})
            else:
                ai_msg = response_message.content
                chat_history.append({"role": "user", "content": user_msg})
                chat_history.append({"role": "assistant", "content": ai_msg})

                if len(chat_history) > 20:
                    chat_history = chat_history[-20:]

                user.set_chat_history(chat_history)
                db.session.commit()

                return jsonify({'reply': ai_msg})
        else:
            raw = response_message.content
            try:
                quest_data = extract_json(raw)
            except (ValueError, json.JSONDecodeError) as parse_err:
                logger.warning("Quick quest JSON parse error: %s — raw: %s", parse_err, raw[:300])
                return jsonify({'error': 'AI returned an unparseable response. Please try again.'}), 500
            return jsonify({'quest': quest_data})

    except Exception as e:
        logger.exception("Error in /api/chat")
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


@api_bp.route('/chat/history', methods=['GET'])
def api_chat_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    raw_history = user.get_chat_history()

    clean_history = []
    for msg in raw_history:
        if msg.get("role") in ["user", "assistant"]:
            if msg.get("role") == "assistant" and not msg.get("content"):
                continue
            clean_history.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })

    return jsonify({'history': clean_history})


@api_bp.route('/quiz/generate', methods=['POST'])
def api_quiz_generate():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data or 'topic' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    topic = data['topic']

    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'AI service configuration error'}), 500

        client = OpenAI(api_key=api_key)

        system_prompt = {
            "role": "system",
            "content": (
                "You are an educational AI assistant that creates engaging multiple-choice quizzes. "
                "Generate a quiz strictly based on the provided topic. Return ONLY a valid JSON object. "
                "The JSON MUST have the structure: "
                '{"questions": [{"question": "...", "options": ["...", "...", "...", "..."], "correct_option_index": 0}]} '
                "Ensure there are exactly 4 options for each question, and the correct_option_index is between 0 and 3. "
                "CRITICAL LANGUAGE RULE: You are strictly restricted to communicating, generating quests, and writing JSON ONLY in Ukrainian or English. If the user prompts you in Ukrainian, generate everything in Ukrainian. If the user prompts you in English, generate everything in English. If the user writes in ANY OTHER language, you must completely ignore that language and respond strictly in Ukrainian."
            )
        }

        user_prompt = {
            "role": "user",
            "content": f"Create a 3-5 question multiple-choice quiz about this specific sub-quest topic: '{topic}'"
        }

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_prompt, user_prompt],
            response_format={"type": "json_object"}
        )

        quiz_data = json.loads(response.choices[0].message.content)
        return jsonify({'quiz': quiz_data.get('questions', [])})

    except Exception as e:
        logger.exception("Error in /api/quiz/generate")
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


@api_bp.route('/quiz/explain', methods=['POST'])
def api_quiz_explain():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    if not data or 'question' not in data or 'user_answer' not in data or 'correct_answer' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    question = data['question']
    user_answer = data['user_answer']
    correct_answer = data['correct_answer']

    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return jsonify({'error': 'AI service configuration error'}), 500

        client = OpenAI(api_key=api_key)

        system_prompt = {
            "role": "system",
            "content": (
                "You are ORIA, an opossum System Guide. Provide a short, punchy, 1-2 sentence explanation. "
                "Explain why the user's answer was wrong (if it was) and why the correct answer is right. "
                "Keep the tone encouraging but slightly edgy. "
                "CRITICAL LANGUAGE RULE: You are strictly restricted to communicating, generating quests, and writing JSON ONLY in Ukrainian or English. If the user prompts you in Ukrainian, generate everything in Ukrainian. If the user prompts you in English, generate everything in English. If the user writes in ANY OTHER language, you must completely ignore that language and respond strictly in Ukrainian."
            )
        }

        user_prompt = {
            "role": "user",
            "content": f"Question: {question}\nUser's Answer: {user_answer}\nCorrect Answer: {correct_answer}\nPlease explain."
        }

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_prompt, user_prompt]
        )

        explanation = response.choices[0].message.content
        return jsonify({'explanation': explanation})

    except Exception as e:
        logger.exception("Error in /api/quiz/explain")
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


@api_bp.route('/store/roulette', methods=['POST'])
def api_store_roulette():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    ROULETTE_COST = 100
    UNLOCKABLE_SKINS = ['skin_1', 'skin_2', 'skin_3', 'skin_4', 'skin_5', 'skin_6']

    if user.level < 3:
        return jsonify({'error': 'Roulette unlocks at Level 3. Keep levelling up!'}), 403

    if user.coins < ROULETTE_COST:
        return jsonify({'error': 'Not enough coins'}), 400

    owned_skins = user.get_owned_skins()
    locked_skins = [s for s in UNLOCKABLE_SKINS if s not in owned_skins]

    if not locked_skins:
        return jsonify({'error': 'All currently available skins are already unlocked!'}), 400

    user.coins -= ROULETTE_COST
    chosen_skin = random.choice(locked_skins)
    owned_skins.append(chosen_skin)
    user.set_owned_skins(owned_skins)

    newly_unlocked = []
    current_achievements = user.get_achievements()
    if 'cyber_spender' not in current_achievements:
        current_achievements.append('cyber_spender')
        user.set_achievements(current_achievements)
        newly_unlocked.append('cyber_spender')

    db.session.commit()

    response_data = {'success': True, 'coins': user.coins, 'unlocked_skin': chosen_skin}
    if newly_unlocked:
        response_data['newly_unlocked'] = newly_unlocked

    return jsonify(response_data)


@api_bp.route('/store/equip', methods=['POST'])
def api_store_equip():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if not data or 'skin_id' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    skin_id = data['skin_id']
    owned_skins = user.get_owned_skins()

    if skin_id not in owned_skins:
        return jsonify({'error': 'Skin not owned'}), 400

    user.equipped_skin = skin_id
    db.session.commit()
    return jsonify({'success': True, 'equipped_skin': skin_id})


@api_bp.route('/leaderboard', methods=['GET'])
def api_leaderboard():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    top_users = User.query.order_by(User.level.desc(), User.xp.desc()).limit(10).all()
    leaderboard = []

    for u in top_users:
        leaderboard.append({
            "username": u.username,
            "level": u.level,
            "xp": u.xp,
            "current_streak": u.current_streak,
            "equipped_title": u.equipped_title or '',
            "is_current_user": u.id == session['user_id']
        })

    return jsonify({'leaderboard': leaderboard})



# ─── Bot API (All routes protected by C-02: require_bot_api_key) ────────────

@api_bp.route('/bot/check_user', methods=['POST'])
@require_bot_api_key
def bot_check_user():
    """Private API route for the bot to check if a Telegram ID is linked."""
    data = request.json
    if not data or 'telegram_id' not in data:
        return jsonify({'error': 'Missing telegram_id'}), 400

    tg_id = str(data['telegram_id'])
    user = User.query.filter_by(telegram_id=tg_id).first()

    if user:
        return jsonify({
            'status': 'success',
            'user_id': user.id,
            'username': user.username,
            'level': user.level,
            'xp': user.xp,
            'coins': user.coins
        }), 200

    return jsonify({'error': 'User not found'}), 404


@api_bp.route('/bot/get_state', methods=['POST'])
@require_bot_api_key
def bot_get_state():
    """Fetch full user state by telegram_id (for bot usage)."""
    data = request.json
    if not data or 'telegram_id' not in data:
        return jsonify({'error': 'Missing telegram_id'}), 400

    user = User.query.filter_by(telegram_id=str(data['telegram_id'])).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'username': user.username,
        'level': user.level,
        'xp': user.xp,
        'coins': user.coins,
        'quests': user.get_quests(),
        'daily_quests': user.get_daily_quests(),
        'current_streak': user.current_streak,
        'achievements': user.get_achievements(),
        'claimed_rewards': user.get_claimed_rewards(),
        'equipped_title': user.equipped_title or ''
    })


@api_bp.route('/bot/register_user', methods=['POST'])
@require_bot_api_key
def bot_register_user():
    """Register a Telegram ID in the global tracker."""
    data = request.json
    if not data or 'telegram_id' not in data:
        return jsonify({'error': 'Missing telegram_id'}), 400

    tg_id = str(data['telegram_id'])
    
    # Check if already registered
    exists = TelegramUser.query.filter_by(telegram_id=tg_id).first()
    if not exists:
        new_tg_user = TelegramUser(telegram_id=tg_id)
        db.session.add(new_tg_user)
        db.session.commit()
        logger.info(f"Registered new Telegram user: {tg_id}")
    
    return jsonify({'success': True}), 200


@api_bp.route('/bot/telegram_ids', methods=['GET'])
@require_bot_api_key
def bot_get_telegram_ids():
    """Fetch telegram IDs based on audience selection."""
    only_linked = request.args.get('only_linked', 'false').lower() == 'true'
    
    if only_linked:
        # Fetch linked IDs from User model
        users = User.query.filter(User.telegram_id.isnot(None)).all()
        telegram_ids = [u.telegram_id for u in users if u.telegram_id]
    else:
        # Fetch all IDs from TelegramUser tracker
        users = TelegramUser.query.all()
        telegram_ids = [u.telegram_id for u in users]
        
    return jsonify({'telegram_ids': telegram_ids})


# ─── Auth ───────────────────────────────────────────────────────────────────

@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid payload'}), 400

    email = data.get('e-mail') or data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        session.permanent = True
        pending_tg_id = session.get('pending_tg_id')
        if pending_tg_id:
            existing_link = User.query.filter_by(telegram_id=pending_tg_id).first()
            if not existing_link:
                user.telegram_id = pending_tg_id
                db.session.commit()
            session.pop('pending_tg_id', None)

        return jsonify({
            'status': 'success',
            'user': {'id': user.id, 'username': user.username}
        }), 200

    return jsonify({'error': 'Invalid email or password!'}), 401


@api_bp.route('/register', methods=['POST'])
def api_register():
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid payload'}), 400

    name = data.get('name')
    email = data.get('e-mail') or data.get('email')
    password = data.get('password')
    pronouns = ", ".join(data.get('pronoun', [])) if isinstance(data.get('pronoun'), list) else data.get('pronoun', '')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password required'}), 400

    # W-04: Password strength validation
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400

    existing_user = User.query.filter(
        (User.username == name) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify({'error': 'Username or email is already in use.'}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=name, email=email, password=hashed_password, pronouns=pronouns)
    db.session.add(new_user)
    db.session.commit()

    session['user_id'] = new_user.id
    session['username'] = new_user.username
    session.permanent = True
    pending_tg_id = session.get('pending_tg_id')
    if pending_tg_id:
        existing_link = User.query.filter_by(telegram_id=pending_tg_id).first()
        if not existing_link:
            new_user.telegram_id = pending_tg_id
            db.session.commit()
        session.pop('pending_tg_id', None)

    return jsonify({
        'status': 'success',
        'user': {'id': new_user.id, 'username': new_user.username}
    }), 200


@api_bp.route('/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success'}), 200

# ─── Bot-specific Endpoints (for Telegram Bot) ───────────────────────────────

@api_bp.route('/bot/user/action', methods=['POST'])
@require_bot_api_key
def bot_user_action():
    data = request.json
    if not data or 'telegram_id' not in data:
        return jsonify({'error': 'Missing telegram_id'}), 400

    user = User.query.filter_by(telegram_id=str(data['telegram_id'])).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if data.get('type') != 'award_xp':
        return jsonify({'error': 'Invalid action type'}), 400

    try:
        amount = int(data.get('amount', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid XP amount'}), 400

    if amount <= 0 or amount > MAX_XP_PER_ACTION:
        return jsonify({'error': f'XP amount must be between 1 and {MAX_XP_PER_ACTION}'}), 400

    user.xp += amount
    user.coins += amount // 2

    leveled_up = False
    while user.xp >= 100:
        user.level += 1
        user.xp -= 100
        leveled_up = True

    db.session.commit()

    return jsonify({
        'success': True,
        'xp': user.xp,
        'coins': user.coins,
        'level': user.level,
        'leveled_up': leveled_up,
        'new_level': user.level if leveled_up else None
    })


@api_bp.route('/bot/user/update', methods=['POST'])
@require_bot_api_key
def bot_user_update():
    data = request.json
    if not data or 'telegram_id' not in data:
        return jsonify({'error': 'Missing telegram_id'}), 400

    user = User.query.filter_by(telegram_id=str(data['telegram_id'])).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'quests' in data:
        user.set_quests(data['quests'])
    if 'daily_quests' in data:
        user.set_daily_quests(data['daily_quests'])
    if 'claimed_rewards' in data:
        user.set_claimed_rewards(data['claimed_rewards'])
    if 'equipped_title' in data:
        user.equipped_title = str(data['equipped_title'])[:64]

    db.session.commit()
    return jsonify({'success': True})


@api_bp.route('/bot/chat', methods=['POST'])
@require_bot_api_key
def bot_chat():
    data = request.json
    if not data or 'telegram_id' not in data or 'message' not in data:
        return jsonify({'error': 'Missing telegram_id or message'}), 400

    user = User.query.filter_by(telegram_id=str(data['telegram_id'])).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    onboarding_context = _build_onboarding_context(user)

    system_prompt = {
        "role": "system",
        "content": (
            "You are ORIA, a Cyberpunk Productivity Assistant. "
            "You are interacting with the user via Telegram. "
            "Act slightly edgy but deeply supportive. "
            "If the user asks to create a quest, use 'create_rpg_quest' tool. "
            "Respond strictly in Ukrainian or English."
            + onboarding_context
        )
    }

    user_msg = data['message']
    chat_history = user.get_chat_history()
    messages = [system_prompt] + chat_history + [{"role": "user", "content": user_msg}]

    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        tools = [CREATE_QUEST_TOOL]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            if tool_call.function.name == "create_rpg_quest":
                quest_args = json.loads(tool_call.function.arguments)
                user_quests = user.get_quests()
                user_quests.append(quest_args)
                user.set_quests(user_quests)

                chat_history.append({"role": "user", "content": user_msg})
                chat_history.append({
                    "role": "assistant",
                    "content": "Quest creation module initialized.",
                    "tool_calls": [tool_call.model_dump()]
                })

                second_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[system_prompt] + chat_history + [{
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "create_rpg_quest",
                        "content": "Quest successfully saved."
                    }]
                )
                final_reply = second_response.choices[0].message.content
                chat_history.append({"role": "assistant", "content": final_reply})
                user.set_chat_history(chat_history[-20:])
                db.session.commit()
                return jsonify({'reply': final_reply, 'quest_added': True})
        else:
            ai_msg = response_message.content
            chat_history.append({"role": "user", "content": user_msg})
            chat_history.append({"role": "assistant", "content": ai_msg})
            user.set_chat_history(chat_history[-20:])
            db.session.commit()
            return jsonify({'reply': ai_msg})
    except Exception as e:
        logger.exception("Error in /api/bot/chat")
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500

@api_bp.route('/bot/leaderboard', methods=['GET'])
@require_bot_api_key
def bot_leaderboard():
    top_users = User.query.order_by(User.level.desc(), User.xp.desc()).limit(10).all()
    leaderboard = []
    for u in top_users:
        leaderboard.append({
            'username': u.username,
            'level': u.level,
            'xp': u.xp,
            'current_streak': u.current_streak,
            'equipped_title': u.equipped_title or ''
        })
    return jsonify({'leaderboard': leaderboard})


@api_bp.route('/bot/user/daily_refresh', methods=['POST'])
@require_bot_api_key
def bot_daily_refresh():
    data = request.json
    if not data or 'telegram_id' not in data:
        return jsonify({'error': 'Missing telegram_id'}), 400

    user = User.query.filter_by(telegram_id=str(data['telegram_id'])).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    _generate_daily_quests(user)

    return jsonify({
        'success': True,
        'daily_quests': user.get_daily_quests()
    })


@api_bp.route('/bot/rewards/claim', methods=['POST'])
@require_bot_api_key
def bot_claim_reward():
    data = request.json
    if not data or 'telegram_id' not in data or 'level' not in data:
        return jsonify({'error': 'Missing telegram_id or level'}), 400

    user = User.query.filter_by(telegram_id=str(data['telegram_id'])).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        req_level = int(data.get('level', 0))
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid level'}), 400

    if req_level not in LEVEL_REWARDS:
        return jsonify({'error': 'Unknown reward level'}), 400

    if user.level < req_level:
        return jsonify({'error': f'You need to be Level {req_level} to claim this reward'}), 403

    claimed = user.get_claimed_rewards()
    if req_level in claimed:
        return jsonify({'error': 'Reward already claimed'}), 409

    reward = LEVEL_REWARDS[req_level]

    if reward['coins'] > 0:
        user.coins += reward['coins']

    claimed.append(req_level)
    user.set_claimed_rewards(claimed)
    db.session.commit()

    return jsonify({
        'success': True,
        'coins': user.coins,
        'claimed_rewards': user.get_claimed_rewards(),
        'unlocked_title': reward['title'],
        'coins_granted': reward['coins'],
    })

@api_bp.route('/bot/miniquest/complete', methods=['POST'])
@require_bot_api_key
def bot_miniquest_complete():
    """Mark a specific sub-task as completed with race-condition protection (W-07)."""
    data = request.json
    if not data or 'telegram_id' not in data or 'global_index' not in data or 'mini_index' not in data:
        return jsonify({'error': 'Missing telegram_id, global_index, or mini_index'}), 400

    user = User.query.filter_by(telegram_id=str(data['telegram_id'])).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    quests = user.get_quests()
    try:
        g_idx = int(data['global_index'])
        m_idx = int(data['mini_index'])
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid index format'}), 400

    if g_idx < 0 or g_idx >= len(quests):
        return jsonify({'error': 'Invalid global quest index'}), 400

    quest = quests[g_idx]
    sub_tasks = quest.get('sub_tasks', [])

    if m_idx < 0 or m_idx >= len(sub_tasks):
        return jsonify({'error': 'Invalid mini-quest index'}), 400

    sub_task = sub_tasks[m_idx]
    if sub_task.get('completed'):
        return jsonify({'error': 'Mini-quest already completed'}), 400

    # 1. Mark mini-quest as completed
    sub_task['completed'] = True

    # 2. Award XP for mini-quest
    xp_gain = sub_task.get('xp_reward', 20)
    user.xp += xp_gain
    user.coins += xp_gain // 2

    # 3. Recalculate global progress
    total_subs = len(sub_tasks)
    done_subs = sum(1 for s in sub_tasks if s.get('completed'))
    quest['progress'] = int((done_subs / total_subs) * 100) if total_subs > 0 else 100

    # 4. If all done, mark global quest as completed
    if quest['progress'] == 100:
        quest['status'] = 'completed'

    # 5. Critical Fix: Inform SQLAlchemy that the JSON list has changed
    user.set_quests(quests)
    flag_modified(user, 'quests')

    # 6. Level up logic
    leveled_up = False
    while user.xp >= 100:
        user.level += 1
        user.xp -= 100
        leveled_up = True

    db.session.commit()

    return jsonify({
        'success': True,
        'xp_gained': xp_gain,
        'new_xp': user.xp,
        'new_level': user.level,
        'leveled_up': leveled_up,
        'quest_progress': quest['progress'],
        'quest_status': quest.get('status', 'active')
    })


# C-08: Fixed — this function was missing its route decorator!
@api_bp.route('/bot/quiz/generate', methods=['POST'])
@require_bot_api_key
def bot_quiz_generate():
    data = request.json
    if not data or 'topic' not in data:
        return jsonify({'error': 'Invalid topic'}), 400

    topic = data['topic']

    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        system_prompt = {
            "role": "system",
            "content": (
                "You are an educational AI assistant. Generate a quiz strictly based on the provided topic. Return ONLY JSON. "
                "Structure: "
                '{"questions": [{"question": "...", "options": ["...", "...", "...", "..."], "correct_option_index": 0}]} '
                "Language: Ukrainian or English (match prompt)."
            )
        }

        user_prompt = {
            "role": "user",
            "content": f"Create a 3 question multiple-choice quiz about: '{topic}'"
        }

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_prompt, user_prompt],
            response_format={"type": "json_object"}
        )

        quiz_data = json.loads(response.choices[0].message.content)
        return jsonify({'quiz': quiz_data.get('questions', [])})

    except Exception as e:
        logger.exception("Error in /api/bot/quiz/generate")
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500


@api_bp.route('/bot/quiz/explain', methods=['POST'])
@require_bot_api_key
def bot_quiz_explain():
    data = request.json
    if not data or 'question' not in data or 'user_answer' not in data or 'correct_answer' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    question = data['question']
    user_answer = data['user_answer']
    correct_answer = data['correct_answer']

    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        system_prompt = {
            "role": "system",
            "content": "You are ORIA. Explain why the user's answer was wrong/correct in 1-2 punchy sentences. Language: Ukrainian or English."
        }

        user_prompt = {
            "role": "user",
            "content": f"Question: {question}\nUser's Answer: {user_answer}\nCorrect Answer: {correct_answer}"
        }

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[system_prompt, user_prompt]
        )

        explanation = response.choices[0].message.content
        return jsonify({'explanation': explanation})

    except Exception as e:
        logger.exception("Error in /api/bot/quiz/explain")
        return jsonify({'error': 'An internal error occurred. Please try again.'}), 500
