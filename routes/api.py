import os
import re
import json
import datetime
import random
from flask import Blueprint, request, jsonify, session
from openai import OpenAI
from models import db, User

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
        "drink water",
        "do a 5 minute warm-up",
        "air out the room",
        "read 10 pages of a book",
        "go for a 15 minute walk",
        "write down three things you're grateful for today"
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
                    'The task MUST be in English. '
                    'Return ONLY a valid JSON object: {"task": "Task name here", "completed": false, "xp_reward": 20}'
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
        print(f"Error generating AI daily task: {e}")
        daily_quests.append({"id": "daily_3", "task": "Smile at your reflection", "completed": False, "xp_reward": 20})

    user.set_daily_quests(daily_quests)
    user.last_daily_date = today_str
    db.session.commit()


# ─── Routes ─────────────────────────────────────────────────────────────────

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
    # Compares calendar DATES only (no time component) to avoid UTC drift bugs.
    # - Already active today  → do nothing
    # - Last active yesterday → increment streak
    # - Older or never        → reset to 1
    if user.last_active_date != today_str:
        if user.last_active_date:
            try:
                last_active = datetime.date.fromisoformat(user.last_active_date)
                delta = (today_date - last_active).days
                if delta == 1:
                    user.current_streak += 1       # exactly yesterday
                else:
                    user.current_streak = 1        # gap detected, reset
            except ValueError:
                user.current_streak = 1
        else:
            user.current_streak = 1               # first ever login

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
            # Always ensure 1 is in the list (Lv1 is baseline)
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
        'unlocked_title': reward['title'],   # None if no title reward
        'coins_granted': reward['coins'],
    })


@api_bp.route('/user/action', methods=['POST'])
def user_action():
    """Authoritative server-side XP, coin, and level computation.
    The frontend sends a validated action type and the reward amount.
    The backend is the single source of truth — the client MUST update
    its local state from the response values returned here.
    """
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

    # Server-side computation — cannot be manipulated by the client
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

    # ── AI Onboarding Memory ──────────────────────────────────────────────────
    # Inject the user's onboarding answers so ORIA knows their goals & interests.
    onboarding = user.get_onboarding_data()
    onboarding_context = ""
    if onboarding and any(onboarding.values()):
        onboarding_context = (
            "\n\nUSER PROFILE (from onboarding — use this to personalise every response):\n"
            f"• About themselves: {onboarding.get('q1', 'N/A')}\n"
            f"• Main goals: {onboarding.get('q2', 'N/A')}\n"
            f"• Favourite hobby: {onboarding.get('q3', 'N/A')}\n"
            f"• Most productive time of day: {onboarding.get('q4', 'N/A')}\n"
            f"• Additional notes: {onboarding.get('q5', 'N/A')}"
        )

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
            "Categorize the quest into [Study & Exams, Project & Coding, Habits & Routine, General]. "
            "Break the main goal into 3-5 high-level 'Modules' (sub_tasks). "
            "For EACH module, generate 4-8 concrete, actionable 'micro_steps'. "
            "MUST USE THE EXACT JSON FORMAT DEFINED BY THE TOOL: "
            "CRITICAL: You have full access to the user's past messages provided in this conversation context. "
            "NEVER say that you do not have memory of past dialogues. Use the history to provide personalized answers."
            + onboarding_context
        )
    }

    if is_quick_quest:
        quick_quest_prompt = {
            "role": "user",
            "content": (
                f"Analyze the user's goal: '{user_msg}'. Auto-categorize it into one of: "
                "[Study & Exams, Project & Coding, Habits & Routine, General]. "
                "Adopt the relevant expert persona (e.g., strict academic tutor for Study). "
                "Break the master goal into 3-5 high-level 'Modules' (sub_tasks). "
                "For EACH module, immediately generate 5-8 concrete, actionable 10-minute 'micro_steps'. "
                "You MUST bypass normal conversation and return the result STRICTLY as a valid JSON object. "
                "The JSON must have the following structure: "
                '{"category": "Study & Exams", "title": "Quest Title", "difficulty": "Hard/Medium/Easy", "progress": 0, "sub_tasks": [{"id": 1, "task": "Module 1: Name", "completed": false, "xp_reward": 50, "micro_steps": [{"id": 101, "task": "Actionable step", "task_description": "A detailed explanation.", "completed": false}, {"id": 102, "task": "Another step", "task_description": "Another explanation.", "completed": false}]}]} '
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
            return jsonify({'error': 'OpenAI API key missing in config.env'}), 500

        client = OpenAI(api_key=api_key)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_rpg_quest",
                    "description": "Create a structured RPG quest and save it to the user's active quests.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string", "description": "Categorize the quest into [Study & Exams, Project & Coding, Habits & Routine, General]."},
                            "title": {"type": "string", "description": "The title of the quest."},
                            "difficulty": {"type": "string", "description": "Difficulty level: Easy, Medium, or Hard."},
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
        ]

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
                print(f"Quick quest JSON parse error: {parse_err}\nRaw: {raw[:300]}")
                return jsonify({'error': 'AI returned an unparseable response. Please try again.'}), 500
            return jsonify({'quest': quest_data})

    except Exception as e:
        print(f"OpenAI Error: {e}")
        return jsonify({'error': str(e)}), 500


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
            return jsonify({'error': 'OpenAI API key missing'}), 500

        client = OpenAI(api_key=api_key)

        system_prompt = {
            "role": "system",
            "content": (
                "You are an educational AI assistant that creates engaging multiple-choice quizzes. "
                "Generate a quiz strictly based on the provided topic. Return ONLY a valid JSON object. "
                "The JSON MUST have the structure: "
                '{"questions": [{"question": "...", "options": ["...", "...", "...", "..."], "correct_option_index": 0}]}'
                "Ensure there are exactly 4 options for each question, and the correct_option_index is between 0 and 3."
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
        print(f"OpenAI Error: {e}")
        return jsonify({'error': str(e)}), 500


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
            return jsonify({'error': 'OpenAI API key missing'}), 500

        client = OpenAI(api_key=api_key)

        system_prompt = {
            "role": "system",
            "content": (
                "You are ORIA, an opossum System Guide. Provide a short, punchy, 1-2 sentence explanation. "
                "Explain why the user's answer was wrong (if it was) and why the correct answer is right. "
                "Keep the tone encouraging but slightly edgy."
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
        print(f"OpenAI Error: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/store/roulette', methods=['POST'])
def api_store_roulette():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    ROULETTE_COST = 100
    UNLOCKABLE_SKINS = ['skin_1', 'skin_2', 'skin_3', 'skin_4', 'skin_5', 'skin_6']

    # Backend guard — cannot be bypassed by client-side manipulation
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
