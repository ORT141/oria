import { OriaState, storeItems } from './state.js';
import {
    saveStateAPI, awardXPActionAPI, claimRewardAPI,
    refreshDailyQuestsAPI, generateQuizAPI, explainQuizAPI,
    spinRouletteAPI, equipSkinAPI, fetchLeaderboardAPI
} from './api.js';

export const translations = {
    en: {
        nav_logout: "Log Out",
        tab_daily: "Daily Quests",
        tab_active: "Active Quests",
        nav_home: "Home",
        nav_rewards: "Rewards",
        nav_stats: "Stats",
        nav_profile: "Profile",
        quick_quest_placeholder: "Enter a quick goal",
        btn_quick_quest: "Quest!",
        tab_roulette: "Skin Roulette",
        tab_skins: "My Skins",
        tab_completed: "Completed Quests",
        tab_stats: "Stats & Leaderboard",
        tab_focus: "Focus Areas",
        tab_achievements: "Achievements",
        tab_rank: "👑 Global XP Rank",
        tab_rewards: "Level Rewards",
        btn_back_to_modules: "← Back to Modules",
        btn_open_module: "Open Module ➔",
        txt_tap_to_expand: "Tap to expand",
        txt_done: "Done",
        msg_quest_completed: "Quest Completed! 🎉",
        msg_xp_earned: "You earned +{XP} XP",
        msg_coins_earned: "and +{COINS} Coins!",
        btn_generate_test: "Generate Mini-Test",
        cat_study: "Study & Exams",
        cat_coding: "Project & Coding",
        cat_habits: "Habits & Routine",
        cat_general: "General",
        txt_loading_titles: "Loading titles...",
        txt_no_quests: "No quests yet. Ask ORIA or use Quick Quest!",
        txt_no_completed: "No completed quests yet.",
        txt_generate_test: "Generate Mini-Test 🧠",
        txt_loading_hackers: "Loading hackers...",
        txt_failed_leaderboard: "Failed to load leaderboard.",
        txt_you: "(You)",
        txt_no_titles_earned: "🔐 No titles earned yet. Claim the Lv. 5 reward in the <a href='#' onclick='window.showRewards(event)' class='text-primary fw-bold'>Rewards tab</a>!",
        txt_equipped_title: "EQUIPPED TITLE",
        txt_welcome: "Welcome",
        txt_coins: "Coins",
        btn_buy: "Buy",
        btn_unlock: "Unlock",
        btn_equip: "Equip",
        txt_equipped: "Equipped",
        txt_pin: "Pin",
        txt_days: "Days",
        txt_current_level: "current level",
        txt_day_streak: "Day streak",
        tab_profile: "Profile",
        chat_placeholder: "Message ORIA...",
        txt_sub_quest_line: "Sub-Quest Chain Line",
        txt_completed: "Completed",
        txt_tasks: "Tasks",
        txt_steps_done: "{X}/{Y} Steps Done",
        txt_xp_on_finish: "+{XP} XP on finish",
        easy: "Easy",
        medium: "Medium",
        hard: "Hard",
        epic: "Epic",
        tasks: "Tasks",
        cat_study: "Study & Exams",
        cat_coding: "Project & Coding",
        cat_habits: "Habits & Routine",
        cat_general: "General",
        btn_buy_skin: "Buy a Skin",
        txt_rewards_subtitle: "Unlock these rewards as you level up your account.",
        txt_level: "Level",
        txt_reward: "Reward",
        txt_status: "Status",
        txt_starter_access: "Starter Access — Daily Quests & Quick Quest",
        txt_unlocked_check: "✓ Unlocked",
        txt_bonus_coins: "+50 Bonus",
        txt_reward_suffix: "Reward",
        txt_exclusive_title: "Exclusive Title:",
        txt_user_profile: "User Profile",
        txt_current_level: "Current Level",
        txt_your_current_level: "Your Current Level",
        txt_day_streak: "Day Streak",
        ach_initiate_title: "Initiate",
        ach_initiate_desc: "Complete 1 Quest",
        ach_on_fire_title: "On Fire",
        ach_on_fire_desc: "3-Day Streak",
        ach_spender_title: "Cyber Spender",
        txt_rewards_footer: "Keep completing quests and daily tasks to level up and claim your rewards!",
        txt_achievement_unlocked: "Achievement Unlocked",
        tap_to_expand: "Tap to expand",
        module_reward: "Module Reward:",
        done: "Done",
        txt_level_prefix: "Level",
        no_title: "(No title)",
        spin_button: "SPIN ROULETTE (Wait 20m)",
        spinning: "Spinning...",
        unlocked: "You unlocked",
        claim: "Claim",
        claimed: "Claimed",
        level_needed: "Lv. {L} needed",
        txt_reward_lv3: "Skin Roulette Access Unlocked",
        txt_reward_lv7: "Free Skin Roulette Spin",
        txt_reward_lv15: "Prestige Badge — Gold Frame on Leaderboard"
    },
    uk: {
        nav_logout: "Вийти",
        tab_daily: "Щоденні квести",
        tab_active: "Активні квести",
        nav_home: "Головна",
        nav_rewards: "Нагороди",
        nav_stats: "Статистика",
        nav_profile: "Профіль",
        quick_quest_placeholder: "Введіть швидку ціль",
        btn_quick_quest: "Квест!",
        tab_roulette: "Рулєтка скінів",
        tab_skins: "Мої скіни",
        tab_completed: "Завершені квести",
        tab_stats: "Статист. та Лідери",
        tab_focus: "Сфери Фокусу",
        tab_achievements: "Досягнення",
        tab_rank: "👑 Глобальний XP Рейтинг",
        tab_rewards: "Нагороди за рівень",
        btn_back_to_modules: "← Назад до модулів",
        btn_open_module: "Відкрити модуль ➔",
        txt_tap_to_expand: "Натисніть, щоб розгорнути",
        txt_done: "Виконано",
        msg_quest_completed: "Квест виконано! 🎉",
        msg_xp_earned: "Ви отримали +{XP} XP",
        msg_coins_earned: "та +{COINS} Coins!",
        btn_generate_test: "Створити міні-тест",
        cat_study: "Навчання та Іспити",
        cat_coding: "Проєкти та Кодинг",
        cat_habits: "Звички та Рутина",
        cat_general: "Загальне",
        txt_loading_titles: "Завантаження титулів...",
        txt_no_quests: "Ще немає квестів. Спитайте ORIA або використайте Швидкий Квест!",
        txt_no_completed: "Ще немає завершених квестів.",
        txt_generate_test: "Створити міні-тест 🧠",
        txt_loading_hackers: "Завантаження хакерів...",
        txt_failed_leaderboard: "Помилка завантаження таблиці лідерів.",
        txt_you: "(Ви)",
        txt_no_titles_earned: "🔐 Ще немає зароблених титулів. Отримайте нагороду 5 рівня на <a href='#' onclick='window.showRewards(event)' class='text-primary fw-bold'>вкладці Нагороди</a>!",
        txt_equipped_title: "АКТИВНИЙ ТИТУЛ",
        txt_welcome: "Вітаємо",
        txt_coins: "Зірки",
        btn_buy: "Купити",
        btn_unlock: "Розблокувати",
        btn_equip: "Одягнути",
        txt_equipped: "Одягнено",
        txt_pin: "Закріпити",
        txt_days: "Днів",
        txt_current_level: "поточний рівень",
        txt_day_streak: "Серія днів",
        tab_profile: "Профіль",
        chat_placeholder: "Написати ORIA...",
        txt_sub_quest_line: "Ланцюжок підквестів",
        txt_completed: "Виконано",
        txt_tasks: "Завдань",
        txt_steps_done: "{X}/{Y} Кроків виконано",
        txt_xp_on_finish: "+{XP} XP за завершення",
        easy: "Легкий",
        medium: "Середній",
        hard: "Складний",
        epic: "Епічний",
        tasks: "Завдань",
        cat_study: "Навчання та Іспити",
        cat_coding: "Проєкти та Кодинг",
        cat_habits: "Звички та Рутина",
        cat_general: "Загальне",
        btn_buy_skin: "Купити скін",
        txt_rewards_subtitle: "Розблоковуйте ці нагороди під час підвищення рівня вашого акаунту.",
        txt_level: "Рівень",
        txt_reward: "Нагорода",
        txt_status: "Статус",
        txt_starter_access: "Початковий доступ — Щоденні квести та Швидкий Квест",
        txt_unlocked_check: "✓ Розблоковано",
        txt_bonus_coins: "+50 Бонусних",
        txt_reward_suffix: "Нагорода",
        txt_exclusive_title: "Ексклюзивний титул:",
        txt_user_profile: "Профіль користувача",
        txt_current_level: "Поточний рівень",
        txt_your_current_level: "Ваш поточний рівень",
        txt_day_streak: "Серія днів",
        ach_initiate_title: "Початківець",
        ach_initiate_desc: "Виконайте 1 Квест",
        ach_on_fire_title: "У вогні",
        ach_on_fire_desc: "Серія з 3 днів",
        ach_spender_title: "Кібервитратник",
        txt_rewards_footer: "Продовжуйте виконувати квести та щоденні завдання, щоб підвищувати рівень та отримувати нагороди!",
        txt_achievement_unlocked: "Досягнення розблоковано",
        tap_to_expand: "Натисніть, щоб розгорнути",
        module_reward: "Нагорода за модуль:",
        done: "Виконано",
        txt_level_prefix: "Рівень",
        no_title: "(Без титулу)",
        spin_button: "КРУТИТИ (Очікуй 20хв)",
        spinning: "Обертається...",
        unlocked: "Ви розблокували",
        claim: "Отримати",
        claimed: "Отримано",
        level_needed: "Потрібен рів. {L}",
        txt_reward_lv3: "Доступ до Рулетки Скінів",
        txt_reward_lv7: "Безкоштовне обертання Рулетки",
        txt_reward_lv15: "Престижний значок — Золота рамка в таблиці лідерів"
    }
};

export function setLanguage(lang) {
    if (!translations[lang]) return;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang][key]) {
            el.innerText = translations[lang][key];
        }
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[lang][key]) {
            el.placeholder = translations[lang][key];
        }
    });
    localStorage.setItem('oria_lang', lang);
}
window.setLanguage = setLanguage;

export function t(key, params = {}) {
    const lang = localStorage.getItem('oria_lang') || 'uk';
    const dict = translations[lang] || translations['en'];
    let str = dict[key] || key;

    // Simple string interpolation for params like +{XP}
    for (const [k, v] of Object.entries(params)) {
        str = str.replace(`{${k}}`, v);
    }
    return str;
}
window.t = t;

document.addEventListener('DOMContentLoaded', () => {
    const langToggle = document.getElementById('languageToggle');
    if (langToggle) {
        const savedLang = localStorage.getItem('oria_lang') || 'uk';
        langToggle.value = savedLang;
        setLanguage(savedLang);

        langToggle.addEventListener('change', (e) => {
            setLanguage(e.target.value);
        });
    }
});

/**
 * Returns the title earned at a given level. Empty string = no title yet.
 */
export function getUserTitle(level) {
    if (level >= 20) return 'System Overlord';
    if (level >= 10) return 'Neural Hacker';
    if (level >= 5) return 'Cyber Initiate';
    return '';
}

class AudioPlayer {
    constructor() {
        this.successSound = new Audio('/static/audio/success.mp3');
        this.levelUpSound = new Audio('/static/audio/levelup.mp3');
    }

    playSuccess() {
        try {
            this.successSound.currentTime = 0;
            this.successSound.play().catch(e => console.warn("Audio autoplay prevented:", e));
        } catch (e) { }
    }

    playLevelUp() {
        try {
            this.levelUpSound.currentTime = 0;
            this.levelUpSound.play().catch(e => console.warn("Audio autoplay prevented:", e));
        } catch (e) { }
    }
}

export const OriaAudio = new AudioPlayer();

export class OriaMascot {
    constructor(elementId, frames) {
        this.element = document.getElementById(elementId);
        if (!this.element) return;

        this.frames = frames;
        this.isAnimating = false;

        this.element.addEventListener('click', () => this.talk());

        this.scheduleBlink();
        this.scheduleTalk();
    }

    setFrame(type) {
        if (!this.element) return;
        if (OriaState && OriaState.equipped_skin !== 'default') return;
        if (this.frames[type]) {
            this.element.src = this.frames[type];
        }
    }

    async blink() {
        if (this.isAnimating) return;
        this.isAnimating = true;

        if (!OriaState || OriaState.equipped_skin === 'default') {
            this.setFrame('blinking');
            await new Promise(r => setTimeout(r, 150));
            this.setFrame('default');
        }

        this.isAnimating = false;
    }

    async talk() {
        if (this.isAnimating) return;
        this.isAnimating = true;

        if (OriaState && OriaState.equipped_skin !== 'default') {
            this.element.classList.add('rocking-animation');
            await new Promise(r => setTimeout(r, 400));
            this.element.classList.remove('rocking-animation');
        } else {
            for (let i = 0; i < 2; i++) {
                this.setFrame('talking');
                await new Promise(r => setTimeout(r, 200));
                this.setFrame('default');
                await new Promise(r => setTimeout(r, 150));
            }
        }

        this.isAnimating = false;
    }

    scheduleBlink() {
        const nextBlink = Math.random() * 3000 + 2000;
        setTimeout(() => {
            this.blink().then(() => this.scheduleBlink());
        }, nextBlink);
    }

    scheduleTalk() {
        const nextTalk = Math.random() * 10000 + 5000;
        setTimeout(() => {
            if (Math.random() > 0.6) {
                this.talk().then(() => this.scheduleTalk());
            } else {
                this.scheduleTalk();
            }
        }, nextTalk);
    }
}

export function updateDOMState() {
    const xpBar = document.getElementById('user-xp-bar');
    const levelEl = document.getElementById('user-level');
    const coinsEl = document.getElementById('user-coins');
    const profLevelEl = document.getElementById('profile-level');
    const profCoinsEl = document.getElementById('profile-coins');
    const profXpBar = document.getElementById('profile-xp-bar');
    const profXpText = document.getElementById('profile-xp-text');

    // XP percentage within the current level (0-99 out of 100 = 0%-99%)
    const xpPct = Math.min(100, Math.max(0, (OriaState.xp / 100) * 100));

    if (xpBar) {
        xpBar.style.width = xpPct + '%';
        xpBar.setAttribute('aria-valuenow', OriaState.xp);
    }
    if (levelEl) levelEl.textContent = OriaState.level;
    if (coinsEl) coinsEl.textContent = OriaState.coins;

    if (profLevelEl) profLevelEl.textContent = OriaState.level;
    if (profCoinsEl) profCoinsEl.textContent = OriaState.coins;
    if (profXpBar) {
        profXpBar.style.width = xpPct + '%';
        profXpBar.setAttribute('aria-valuenow', OriaState.xp);
    }
    if (profXpText) profXpText.textContent = OriaState.xp;

    // Also refresh the rewards-level display if visible
    const rewardsLevelEl = document.getElementById('rewards-current-level');
    if (rewardsLevelEl) rewardsLevelEl.textContent = OriaState.level;

    updateGlobalMascot();
}

export async function addXP(amount) {
    // Optimistic update for instant UI feedback
    OriaState.xp += amount;
    OriaState.coins += Math.floor(amount / 2);
    const tentativeLevelUp = OriaState.xp >= 100;
    if (tentativeLevelUp) {
        OriaState.level += Math.floor(OriaState.xp / 100);
        OriaState.xp = OriaState.xp % 100;
    }
    updateDOMState();

    // Server is the authority — sync back the real values
    try {
        const data = await awardXPActionAPI(amount);
        // Overwrite local state with authoritative server values
        OriaState.xp = data.xp;
        OriaState.coins = data.coins;
        OriaState.level = data.level;
        updateDOMState();

        if (data.leveled_up) {
            OriaAudio.playLevelUp();
            const newLevelEl = document.getElementById('newLevelText');
            if (newLevelEl) {
                newLevelEl.textContent = data.new_level;
                const levelModalEl = document.getElementById('levelUpModal');
                if (window.bootstrap) {
                    let levelModal = window.bootstrap.Modal.getInstance(levelModalEl);
                    if (!levelModal) levelModal = new window.bootstrap.Modal(levelModalEl);
                    levelModal.show();
                }
            }
        }
    } catch (err) {
        console.error('Failed to sync XP with server — UI may be ahead of DB:', err);
    }
}

export function renderQuests() {
    const container = document.getElementById('quests-container');
    const emptyStateHTML = `
        <div class="empty-state text-center p-5 mt-4" style="background: var(--card-bg-solid); border: 1px dashed var(--glass-border-solid); border-radius: var(--radius-lg);">
            <img src="/static/img/IMG_8435.PNG" alt="Sleeping Mascot" width="100" style="opacity: 0.7; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05));" class="mb-3">
            <h5 class="fw-bold" style="color: var(--text-main);">The opossum is playing dead...</h5>
            <p class="text-muted small mb-0 fw-semibold">No active quests found. Enter a quick goal above to wake him up and earn XP!</p>
        </div>
    `;

    if (!OriaState.quests || OriaState.quests.length === 0) {
        container.innerHTML = emptyStateHTML;
        return;
    }

    container.innerHTML = '';
    let activeQuestsCount = 0;

    OriaState.quests.forEach((quest, index) => {
        let completedTasks = 0;
        let totalTasks = 0;
        quest.sub_tasks.forEach(t => {
            if (t.micro_steps && t.micro_steps.length > 0) {
                totalTasks += t.micro_steps.length;
                completedTasks += t.micro_steps.filter(m => m.completed).length;
            } else {
                totalTasks += 1;
                if (t.completed) completedTasks += 1;
            }
        });
        const progress = Math.round((completedTasks / totalTasks) * 100) || 0;

        if (progress >= 100) return;
        activeQuestsCount++;

        const card = document.createElement('div');
        card.className = 'quest-card p-3 mb-2 shadow-sm rounded-3 border';
        card.style.cursor = 'pointer';
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="fw-bold mb-0 text-dark">${quest.title}</h6>
                <span class="badge" style="background: var(--accent-blue);">${quest.difficulty}</span>
            </div>
            <div class="progress mt-2 border" style="height: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
              <div class="progress-bar" role="progressbar" style="width: ${progress}%; background: var(--accent-blue);"></div>
            </div>
            <div class="d-flex justify-content-between mt-2 small text-muted">
                <span>${completedTasks}/${totalTasks} Tasks</span>
                <span class="fw-bold">${progress}%</span>
            </div>
        `;

        card.addEventListener('click', () => openQuestModal(index));
        container.appendChild(card);
    });

    if (activeQuestsCount === 0) {
        container.innerHTML = emptyStateHTML;
    }
}

export function renderDailyQuests() {
    const container = document.getElementById('daily-quests-container');
    if (!container) return;

    container.innerHTML = '';
    const dailyQuests = OriaState.daily_quests || [];

    if (dailyQuests.length === 0) {
        container.innerHTML = '<p class="text-muted small text-center my-2">No daily quests generated yet.</p>';
        return;
    }

    dailyQuests.forEach((quest) => {
        const item = document.createElement('div');
        item.className = `daily-quest-item d-flex align-items-center p-2 rounded-3 ${quest.completed ? 'completed-daily' : ''}`;
        item.style.transition = 'all 0.3s ease';

        const isChecked = quest.completed ? 'checked disabled' : '';

        item.innerHTML = `
            <div class="form-check m-0 p-0 d-flex align-items-center w-100" style="cursor: ${quest.completed ? 'default' : 'pointer'};">
                <input class="form-check-input me-3" type="checkbox" value="" id="dailyCheck_${quest.id}" style="width: 1.25em; height: 1.25em; cursor: pointer; flex-shrink: 0;" ${isChecked}>
                <label class="form-check-label flex-grow-1 daily-task-label ${quest.completed ? 'text-decoration-line-through text-muted' : 'fw-semibold text-dark'}" 
                       for="dailyCheck_${quest.id}" 
                       style="cursor: ${quest.completed ? 'default' : 'pointer'}; font-size: 0.95rem; user-select: none;">
                    ${quest.task}
                </label>
                <span class="badge rounded-pill ms-2" style="background: var(--accent-blue); font-size: 0.75rem;">+${quest.xp_reward} XP</span>
            </div>
        `;

        if (!quest.completed) {
            item.addEventListener('click', (e) => {
                if (item.classList.contains('processing-complete')) return;
                const checkbox = item.querySelector('input');
                if (e.target.tagName !== 'INPUT') {
                    checkbox.checked = !checkbox.checked;
                }
                if (checkbox.checked) {
                    item.classList.add('processing-complete');
                    completeDailyQuest(quest.id, item);
                }
            });
        }

        container.appendChild(item);
    });
}

async function completeDailyQuest(questId, itemElement) {
    const dailyQuests = OriaState.daily_quests;
    const questIndex = dailyQuests.findIndex(q => q.id === questId);

    if (questIndex === -1 || dailyQuests[questIndex].completed) return;

    // Prevent double-clicks during async save
    itemElement.classList.add('processing-complete');
    OriaAudio.playSuccess();

    const label = itemElement.querySelector('.daily-task-label');
    label.classList.remove('text-dark', 'fw-semibold');
    label.classList.add('text-muted', 'text-decoration-line-through');

    const xpReward = dailyQuests[questIndex].xp_reward;

    // Mark complete in local state
    dailyQuests[questIndex].completed = true;

    try {
        // RACE CONDITION FIX: persist completion to backend FIRST,
        // then award XP only after the server confirms the save.
        await saveStateAPI();
        await addXP(xpReward);
    } catch (err) {
        // Revert local state if either save fails
        console.error('Failed to save daily quest completion:', err);
        dailyQuests[questIndex].completed = false;
    }

    renderDailyQuests();
}

export function refreshDailyQuestsHandler(btnElement) {
    if (btnElement) {
        btnElement.disabled = true;
        const icon = btnElement.querySelector('svg');
        if (icon) icon.classList.add('fa-spin', 'text-primary');
        btnElement.style.transform = 'rotate(180deg)';
        btnElement.style.transition = 'transform 0.5s ease';
    }

    const container = document.getElementById('daily-quests-container');
    if (container) container.innerHTML = '<p class="text-muted small text-center my-2">Regenerating quests...</p>';

    refreshDailyQuestsAPI()
        .then(data => {
            if (data.success) {
                OriaState.daily_quests = data.daily_quests;
            }
        })
        .catch(err => console.error(err))
        .finally(() => {
            if (btnElement) {
                btnElement.disabled = false;
                btnElement.style.transform = 'rotate(360deg)';
                const icon = btnElement.querySelector('svg');
                if (icon) icon.classList.remove('text-primary');
                setTimeout(() => { btnElement.style.transform = 'none'; btnElement.style.transition = 'none'; }, 500);
            }
            renderDailyQuests();
        });
}

export function openQuestModal(index) {
    const quest = OriaState.quests[index];
    document.getElementById('questModalTitle').textContent = quest.title;
    document.getElementById('questModalDifficulty').textContent = window.t(quest.difficulty) || quest.difficulty;

    let completedTasks = 0;
    let totalTasks = 0;
    quest.sub_tasks.forEach(t => {
        if (t.micro_steps && t.micro_steps.length > 0) {
            totalTasks += t.micro_steps.length;
            completedTasks += t.micro_steps.filter(m => m.completed).length;
        } else {
            totalTasks += 1;
            if (t.completed) completedTasks += 1;
        }
    });
    const progress = Math.round((completedTasks / totalTasks) * 100) || 0;

    document.getElementById('questProgressText').textContent = `${progress}% ${window.t('txt_completed')}`;
    document.getElementById('questModalProgress').style.width = `${progress}%`;

    const list = document.getElementById('questChainList');
    list.className = 'quest-chain-container position-relative ps-3';
    if (list.previousElementSibling) list.previousElementSibling.style.display = 'block';

    list.innerHTML = '';

    quest.sub_tasks.forEach((task, tIndex) => {
        const item = document.createElement('div');
        item.className = `quest-chain-item ${task.completed ? 'completed' : ''}`;

        let mTotal = task.micro_steps ? task.micro_steps.length : 1;
        let mDone = task.micro_steps ? task.micro_steps.filter(m => m.completed).length : (task.completed ? 1 : 0);

        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center w-100" style="cursor: pointer;">
                <div>
                    <h6 class="fw-bold mb-1 ${task.completed ? 'text-decoration-line-through text-muted' : 'text-dark'}">${task.task}</h6>
                    <small class="text-muted fw-bold" style="color: var(--accent-pink) !important;">${window.t('txt_steps_done', { X: mDone, Y: mTotal })} • ${window.t('txt_xp_on_finish', { XP: task.xp_reward || 50 })}</small>
                </div>
                <div class="d-flex align-items-center gap-2">
                    ${task.completed ? `<span class="text-success fw-bold">✓ ${window.t('done')}</span>` : ''}
                    <button class="btn btn-sm btn-outline-info rounded-pill px-3">${window.t('btn_open_module')}</button>
                </div>
            </div>
        `;

        item.addEventListener('click', () => {
            openModuleView(index, tIndex);
        });

        list.appendChild(item);
    });

    const modalEl = document.getElementById('questChainModal');
    if (window.bootstrap) {
        let modal = window.bootstrap.Modal.getInstance(modalEl);
        if (!modal) {
            modal = new window.bootstrap.Modal(modalEl);
        }
        modal.show();
    }
}

function openModuleView(qIndex, tIndex) {
    const quest = OriaState.quests[qIndex];
    const task = quest.sub_tasks[tIndex];

    document.getElementById('questModalTitle').textContent = quest.title + ' > ' + task.task;

    const list = document.getElementById('questChainList');
    list.className = '';
    if (list.previousElementSibling) list.previousElementSibling.style.display = 'none';

    list.innerHTML = `
        <div>
            <button class="btn btn-sm btn-secondary mb-3 rounded-pill fw-bold shadow-sm px-3 border-0" style="background: rgba(0,0,0,0.05); color: var(--text-main);" id="btnBackToModules">
                ${window.t('btn_back_to_modules')}
            </button>
            <h4 class="mb-2 text-info fw-bold">${task.task}</h4>
            ${task.task_description ? `<p class="text-muted small mb-4">${task.task_description}</p>` : '<div class="mb-4"></div>'}
            <div id="moduleStepsContainer" class="micro-steps-container"></div>
        </div>
    `;

    document.getElementById('btnBackToModules').addEventListener('click', () => {
        openQuestModal(qIndex);
    });

    const stepsContainer = document.getElementById('moduleStepsContainer');

    if (task.micro_steps && task.micro_steps.length > 0) {
        task.micro_steps.forEach((mStep, mIdx) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = `p-3 mb-3 glass-card shadow-sm position-relative ${mStep.completed ? 'opacity-75' : ''}`;
            stepDiv.style.borderRadius = '12px';
            stepDiv.style.border = '1px solid rgba(0,0,0,0.05)';
            stepDiv.style.background = mStep.completed ? 'rgba(0,0,0,0.02)' : 'var(--card-bg)';

            const isChecked = mStep.completed ? 'checked disabled' : '';

            // Header: Checkbox + Title (Clickable body-toggle logic will be bound to header)
            const headerHtml = `
                <div class="d-flex align-items-start justify-content-between step-header" style="cursor: pointer;">
                    <div class="d-flex align-items-start flex-grow-1 pe-2">
                        <input class="form-check-input micro-step-checkbox me-3 shadow-sm border-2" type="checkbox" id="mStep_${qIndex}_${tIndex}_${mIdx}" data-qindex="${qIndex}" data-tindex="${tIndex}" data-mindex="${mIdx}" style="width: 1.4em; height: 1.4em; cursor: ${mStep.completed ? 'default' : 'pointer'}; flex-shrink: 0; margin-top: 0.15rem;" ${isChecked} onclick="event.stopPropagation();">
                        <div class="flex-grow-1">
                            <label class="form-check-label w-100 ${mStep.completed ? 'text-decoration-line-through text-muted' : 'fw-bold text-dark'}" style="cursor: pointer; font-size: 1.05rem; user-select: none;">
                                ${mStep.task}
                            </label>
                            ${mStep.completed ? '' : '<span class="badge rounded-pill mt-1 badge-xp shadow-sm" style="background: var(--accent-blue); opacity: 0.85;">+10 XP</span>'}
                        </div>
                    </div>
                    ${mStep.completed
                    ? '<span class="text-success fw-bold flex-shrink-0 mt-1" style="font-size: 0.9rem;">✓</span>'
                    : `<button class="btn btn-sm text-white rounded-pill px-3 py-1 shadow-sm flex-shrink-0 mt-1 micro-btn-complete" style="background: var(--primary-gradient); font-size: 0.75rem; font-weight: bold;" data-qindex="${qIndex}" data-tindex="${tIndex}" data-mindex="${mIdx}" onclick="event.stopPropagation();">Complete</button>`
                }
                </div>
            `;

            // Body: Description (Hidden by default)
            let bodyHtml = '';
            if (mStep.task_description || mStep.quiz_data) {
                bodyHtml = `
                    <div class="step-body mt-3 pt-2 border-top border-opacity-25" style="display: none;">
                        ${mStep.task_description ? `<p class="text-muted small mb-0 ${mStep.completed ? 'text-decoration-line-through' : ''}">${mStep.task_description}</p>` : ''}
                        
                        ${/* Micro-step specific quiz rendering space */ ''}
                        <div class="micro-quiz-container mt-3" id="micro-quiz-${qIndex}-${tIndex}-${mIdx}">
                `;

                if (mStep.quiz_data) {
                    if (mStep.quiz_score !== undefined) {
                        bodyHtml += `
                            <div class="glass-card p-3 shadow-sm border-success">
                                <h6 class="text-success fw-bold text-center mb-3" style="font-size: 0.9rem;">Quiz Completed! Score: ${mStep.quiz_score}%</h6>
                                ${mStep.quiz_data.map((q, qIdx) => {
                            const userAnsIdx = mStep.user_answers[qIdx];
                            const isCorrect = userAnsIdx === q.correct_option_index;
                            return `
                                        <div class="mb-3">
                                            <div class="fw-bold text-dark mb-1" style="font-size: 0.85rem;">${qIdx + 1}. ${q.question}</div>
                                            <div class="ps-2 border-start border-2 border-primary border-opacity-25">
                                                ${q.options.map((opt, oIdx) => `
                                                    <div class="form-check mb-1">
                                                        <input type="radio" id="mq-${qIndex}-${tIndex}-${mIdx}-${qIdx}-o-${oIdx}-done" ${oIdx === userAnsIdx ? 'checked' : ''} disabled class="d-none">
                                                        <label class="fw-semibold ${oIdx === q.correct_option_index ? 'text-success' : (oIdx === userAnsIdx ? 'text-danger' : 'text-muted')}" style="opacity: 0.9; font-size: 0.8rem;">
                                                            ${oIdx === q.correct_option_index ? '✓' : (oIdx === userAnsIdx ? '✗' : '·')} ${opt}
                                                        </label>
                                                    </div>
                                                `).join('')}
                                            </div>
                                            ${!isCorrect ? `<button class="btn btn-sm btn-outline-primary mt-1 rounded-pill px-2 py-0 fw-bold micro-btn-explain" style="font-size: 0.75rem;" data-qindex="${qIndex}" data-tindex="${tIndex}" data-mindex="${mIdx}" data-questionidx="${qIdx}">Explain Why</button>` : ''}
                                            <div class="mt-2 p-2 bg-light rounded border micro-explain-box" id="micro-explain-box-${qIndex}-${tIndex}-${mIdx}-${qIdx}" style="display: none; font-size: 0.8rem;"></div>
                                        </div>
                                    `;
                        }).join('')}
                                <div class="text-center mt-2 border-top pt-2">
                                    <button class="btn btn-sm btn-outline-danger rounded-pill fw-bold px-3 py-1 micro-btn-new-test" style="font-size: 0.8rem;" data-qindex="${qIndex}" data-tindex="${tIndex}" data-mindex="${mIdx}">Generate New Test</button>
                                </div>
                            </div>
                        `;
                    } else {
                        bodyHtml += `
                            <div class="p-3 glass-card shadow-sm border border-primary border-opacity-25">
                                <h6 class="fw-bold mb-2 text-primary text-center" style="font-size: 0.85rem;">AI generated Mini-Test</h6>
                                <div id="micro-quiz-form-${qIndex}-${tIndex}-${mIdx}">
                                    ${mStep.quiz_data.map((q, qIdx) => `
                                        <div class="mb-3 micro-quiz-question" data-correct="${q.correct_option_index}">
                                            <div class="fw-bold text-dark mb-1" style="font-size: 0.85rem;">${qIdx + 1}. ${q.question}</div>
                                            <div class="d-flex flex-column gap-1">
                                                ${q.options.map((opt, oIdx) => `
                                                    <input type="radio" name="mq-${qIndex}-${tIndex}-${mIdx}-${qIdx}" id="mq-${qIndex}-${tIndex}-${mIdx}-${qIdx}-o-${oIdx}" value="${oIdx}" class="micro-quiz-option-input d-none">
                                                    <label for="mq-${qIndex}-${tIndex}-${mIdx}-${qIdx}-o-${oIdx}" class="p-2 border rounded bg-white text-dark shadow-sm" style="cursor: pointer; font-size: 0.8rem;">
                                                        ${opt}
                                                    </label>
                                                `).join('')}
                                            </div>
                                        </div>
                                    `).join('')}
                                    <button class="btn btn-primary btn-sm w-100 rounded-pill fw-bold mt-2 shadow micro-btn-submit-test" data-qindex="${qIndex}" data-tindex="${tIndex}" data-mindex="${mIdx}">Submit Test</button>
                                </div>
                            </div>
                        `;
                    }
                } else if (!mStep.completed) {
                    bodyHtml += `
                        <div class="mt-2 text-end">
                            <button class="btn btn-sm btn-outline-primary rounded-pill px-3 py-1 fw-bold micro-btn-generate-quiz" style="font-size: 0.8rem;" data-qindex="${qIndex}" data-tindex="${tIndex}" data-mindex="${mIdx}">
                                ${window.t('btn_generate_test')}
                            </button>
                        </div>
                    `;
                }

                bodyHtml += `
                        </div>
                    </div>
                `;
            }

            stepDiv.innerHTML = headerHtml + bodyHtml;

            // Expand/Collapse Logic: clicking header toggles body visibility
            const headerEl = stepDiv.querySelector('.step-header');
            const bodyEl = stepDiv.querySelector('.step-body');
            if (bodyEl) {
                headerEl.addEventListener('click', (e) => {
                    // CRITICAL FIX: Do nothing if the user specifically clicked the checkbox
                    if (e.target.tagName.toLowerCase() === 'input' && e.target.type === 'checkbox') {
                        return;
                    }
                    if (e.target.classList.contains('micro-step-checkbox')) return; // Fallback

                    if (bodyEl.style.display === 'none') {
                        bodyEl.style.display = 'block';
                    } else {
                        bodyEl.style.display = 'none';
                    }
                });
            }

            stepsContainer.appendChild(stepDiv);
        });
    } else {
        stepsContainer.innerHTML = `
            <div class="d-flex justify-content-between align-items-center p-3 glass-card rounded-3 mb-3 border border-primary border-opacity-25">
                <span class="fw-bold text-dark">${window.t('module_reward')}</span>
                ${!task.completed ? `<button class="btn btn-sm text-white rounded-pill px-3 py-1 btn-complete-task fw-bold shadow-sm" style="background: var(--primary-gradient);" data-qindex="${qIndex}" data-tindex="${tIndex}">Complete (+${task.xp_reward || 50} XP)</button>` : `<span class="text-success fw-bold">✓ ${window.t('done')}</span>`}
            </div>
        `;
    }

    // append quiz directly to the list container logic (it originally appended to list)
    // we'll append to list outside the main div if needed, or inside the wrapper
    const wrapper = list.firstElementChild;


    let quizHtml = '';
    if (task.quiz_data) {
        if (task.quiz_score !== undefined) {
            quizHtml += `<div class="quiz-container glass-card p-3 shadow-sm border-success mt-4">
                <h6 class="text-success fw-bold text-center mb-3">Quiz Completed! Score: ${task.quiz_score}%</h6>
                ${task.quiz_data.map((q, qIdx) => {
                const userAnsIdx = task.user_answers[qIdx];
                const isCorrect = userAnsIdx === q.correct_option_index;
                return `
                    <div class="mb-4">
                        <div class="quiz-question-title fw-bold text-dark mb-2">${qIdx + 1}. ${q.question}</div>
                        <div class="quiz-options-list ps-3 border-start border-2 border-primary border-opacity-25">
                            ${q.options.map((opt, oIdx) => `
                                <div class="form-check mb-1">
                                    <input type="radio" id="q-${qIndex}-${tIndex}-${qIdx}-o-${oIdx}-done" ${oIdx === userAnsIdx ? 'checked' : ''} disabled class="quiz-option-input d-none">
                                    <label for="q-${qIndex}-${tIndex}-${qIdx}-o-${oIdx}-done" class="quiz-option-label fw-semibold small ${oIdx === q.correct_option_index ? 'correct-answer text-success' : (oIdx === userAnsIdx ? 'wrong-answer text-danger' : 'text-muted')}" style="opacity: 0.9; cursor: default;">
                                        ${oIdx === q.correct_option_index ? '✓' : (oIdx === userAnsIdx ? '✗' : '·')} ${opt}
                                    </label>
                                </div>
                            `).join('')}
                        </div>
                        ${!isCorrect ? `<button class="btn btn-sm btn-outline-primary mt-2 rounded-pill px-3 fw-bold btn-explain" data-qindex="${qIndex}" data-tindex="${tIndex}" data-questionidx="${qIdx}">Explain Why</button>` : ''}
                        <div class="ai-explanation-box mt-2 p-2 bg-light rounded small border" id="explain-box-${qIndex}-${tIndex}-${qIdx}" style="display: none;"></div>
                    </div>
                    `;
            }).join('')}
                <div class="text-center mt-3 border-top pt-3">
                    <button class="btn btn-sm btn-outline-danger rounded-pill fw-bold px-4 btn-new-test" data-qindex="${qIndex}" data-tindex="${tIndex}">Generate New Test</button>
                </div>
            </div>`;
        } else {
            quizHtml += `<div class="quiz-container p-3 glass-card shadow-sm mt-4 border border-primary border-opacity-25">
                <h6 class="fw-bold mb-3 text-primary text-center">AI generated Mini-Test</h6>
                <div id="quiz-form-${qIndex}-${tIndex}">
                    ${task.quiz_data.map((q, qIdx) => `
                    <div class="mb-4 quiz-question" data-correct="${q.correct_option_index}">
                        <div class="quiz-question-title fw-bold text-dark mb-2">${qIdx + 1}. ${q.question}</div>
                        <div class="quiz-options-list d-flex flex-column gap-2">
                            ${q.options.map((opt, oIdx) => `
                                <input type="radio" name="q-${qIndex}-${tIndex}-${qIdx}" id="q-${qIndex}-${tIndex}-${qIdx}-o-${oIdx}" value="${oIdx}" class="quiz-option-input d-none">
                                <label for="q-${qIndex}-${tIndex}-${qIdx}-o-${oIdx}" class="quiz-option-label p-2 border rounded-3 bg-white text-dark shadow-sm" style="cursor: pointer; font-size: 0.9rem;">
                                    ${opt}
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    `).join('')}
                    <button class="btn btn-primary w-100 rounded-pill fw-bold mt-3 shadow btn-submit-test" data-qindex="${qIndex}" data-tindex="${tIndex}">Submit Test</button>
                </div>
            </div>`;
        }
    } else if (task.completed) {
        quizHtml += `
            <div class="text-center mt-4 pt-3 border-top border-opacity-50">
                <button class="btn btn-outline-primary rounded-pill px-4 py-2 fw-bold shadow-sm btn-generate-quiz" data-qindex="${qIndex}" data-tindex="${tIndex}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="me-1 mb-1"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                    ${window.t('btn_generate_test')}
                </button>
            </div>
        `;
    }

    if (quizHtml) {
        const quizContainer = document.createElement('div');
        quizContainer.innerHTML = quizHtml;
        wrapper.appendChild(quizContainer);
    }

    list.querySelectorAll('.micro-btn-generate-quiz').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget;
            const mIdx = parseInt(target.getAttribute('data-mindex'));

            const originalText = target.innerHTML;
            target.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            target.disabled = true;

            const mStep = task.micro_steps[mIdx];

            generateQuizAPI(mStep.task)
                .then(data => {
                    if (data.quiz && data.quiz.length > 0) {
                        mStep.quiz_data = data.quiz;
                        saveStateAPI();
                        openModuleView(qIndex, tIndex);
                    } else {
                        alert('Error generating test.');
                        target.innerHTML = originalText;
                        target.disabled = false;
                    }
                })
                .catch(err => {
                    alert('Connection error.');
                    target.innerHTML = originalText;
                    target.disabled = false;
                });
        });
    });

    list.querySelectorAll('.micro-step-checkbox').forEach(chk => {
        chk.addEventListener('change', async (e) => {
            e.stopPropagation(); // Prevent this click from expanding/collapsing the body

            const mIdx = parseInt(e.target.getAttribute('data-mindex'));
            const m = task.micro_steps[mIdx];

            if (m.completed) return;
            m.completed = true;
            e.target.disabled = true;

            const parentDiv = e.target.closest('.glass-card');
            parentDiv.classList.add('opacity-75');
            parentDiv.style.background = 'rgba(0,0,0,0.02)';

            const label = e.target.nextElementSibling.querySelector('label');
            if (label) {
                label.classList.remove('fw-bold', 'text-dark');
                label.classList.add('text-decoration-line-through', 'text-muted');
                label.style.cursor = 'default';
            }

            const bodyEl = parentDiv.querySelector('.step-body');
            if (bodyEl && bodyEl.querySelector('p')) {
                bodyEl.querySelector('p').classList.add('text-decoration-line-through');
            }

            const badge = e.target.nextElementSibling.querySelector('.badge-xp');
            if (badge) badge.style.display = 'none';

            await addXP(10);

            if (task.micro_steps.every(step => step.completed) && !task.completed) {
                task.completed = true;
                if (task.xp_reward) {
                    await addXP(task.xp_reward);
                }
            }

            await checkQuestCompletion(qIndex);

            // Recalculate Quest Progress
            const overarchingQuest = OriaState.quests[qIndex];
            if (overarchingQuest && overarchingQuest.sub_tasks) {
                let completedTaskCount = 0;
                let totalTaskCount = 0;
                overarchingQuest.sub_tasks.forEach(t => {
                    if (t.micro_steps && t.micro_steps.length > 0) {
                        totalTaskCount += t.micro_steps.length;
                        completedTaskCount += t.micro_steps.filter(ms => ms.completed).length;
                    } else {
                        totalTaskCount += 1;
                        if (t.completed) completedTaskCount += 1;
                    }
                });
                const progressPercentage = Math.round((completedTaskCount / totalTaskCount) * 100) || 0;
                const progressTextEl = document.getElementById('questProgressText');
                if (progressTextEl) progressTextEl.textContent = `${progressPercentage}% ${window.t('txt_completed')}`;
                const progressBarEl = document.getElementById('questModalProgress');
                if (progressBarEl) progressBarEl.style.width = `${progressPercentage}%`;
            }

            try {
                await saveStateAPI();
                openModuleView(qIndex, tIndex);
                renderQuests();
            } catch (err) {
                console.error('Failed to save micro-step completion', err);
            }
        });

        // Ensure standard clicks on the checkbox ALSO stop bubbling just to be safe
        chk.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });

    list.querySelectorAll('.micro-btn-complete').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const btnEl = e.currentTarget;
            btnEl.disabled = true;
            btnEl.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            const mIdx = parseInt(btnEl.getAttribute('data-mindex'));
            const chk = document.getElementById(`mStep_${qIndex}_${tIndex}_${mIdx}`);
            if (chk && !chk.checked) {
                chk.checked = true;
                chk.dispatchEvent(new Event('change'));
            }
        });
    });

    list.querySelectorAll('.micro-btn-submit-test').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const mIdx = parseInt(e.target.getAttribute('data-mindex'));
            const mStep = task.micro_steps[mIdx];

            const container = document.getElementById(`micro-quiz-form-${qIndex}-${tIndex}-${mIdx}`);
            const questions = container.querySelectorAll('.micro-quiz-question');

            let correctCount = 0;
            let userAnswers = [];
            let allAnswered = true;

            questions.forEach((qDiv, idx) => {
                const selected = qDiv.querySelector(`input[name="mq-${qIndex}-${tIndex}-${mIdx}-${idx}"]:checked`);
                if (!selected) {
                    allAnswered = false;
                } else {
                    const selVal = parseInt(selected.value);
                    const correctVal = parseInt(qDiv.getAttribute('data-correct'));
                    userAnswers.push(selVal);
                    if (selVal === correctVal) correctCount++;
                }
            });

            if (!allAnswered) {
                alert('Please answer all questions before submitting.');
                return;
            }

            const percentage = Math.round((correctCount / questions.length) * 100);
            mStep.quiz_score = percentage;
            mStep.user_answers = userAnswers;

            saveStateAPI();
            openModuleView(qIndex, tIndex);
        });
    });

    list.querySelectorAll('.micro-quiz-option-input:not([disabled])').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const groupName = e.target.name;
            document.querySelectorAll(`input[name="${groupName}"]`).forEach(r => {
                const lbl = document.querySelector(`label[for="${r.id}"]`);
                if (r.checked) {
                    lbl.classList.remove('bg-white', 'text-dark');
                    lbl.classList.add('bg-primary', 'text-white', 'border-primary');
                } else {
                    lbl.classList.remove('bg-primary', 'text-white', 'border-primary');
                    lbl.classList.add('bg-white', 'text-dark');
                }
            });
        });
    });

    list.querySelectorAll('.micro-btn-new-test').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const mIdx = parseInt(e.target.getAttribute('data-mindex'));
            const mStep = task.micro_steps[mIdx];

            delete mStep.quiz_data;
            delete mStep.quiz_score;
            delete mStep.user_answers;

            saveStateAPI();
            openModuleView(qIndex, tIndex);
        });
    });

    list.querySelectorAll('.micro-btn-explain').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget;
            const mIdx = parseInt(target.getAttribute('data-mindex'));
            const questionIdx = parseInt(target.getAttribute('data-questionidx'));

            const mStep = task.micro_steps[mIdx];
            const qData = mStep.quiz_data[questionIdx];
            const userAnswerText = qData.options[mStep.user_answers[questionIdx]];
            const correctAnswerText = qData.options[qData.correct_option_index];

            const explainBox = document.getElementById(`micro-explain-box-${qIndex}-${tIndex}-${mIdx}-${questionIdx}`);

            target.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            target.disabled = true;

            explainQuizAPI(qData.question, userAnswerText, correctAnswerText)
                .then(data => {
                    target.style.display = 'none';
                    explainBox.innerHTML = window.DOMPurify.sanitize(`<strong>ORIA:</strong> ${data.explanation}`);
                    explainBox.style.display = 'block';
                })
                .catch(err => {
                    alert('Error loading explanation.');
                    target.innerHTML = 'Explain Why';
                    target.disabled = false;
                });
        });
    });

    if (list.querySelector('.btn-complete-task')) {
        list.querySelector('.btn-complete-task').addEventListener('click', (e) => {
            completeTask(qIndex, tIndex);
            openModuleView(qIndex, tIndex);
        });
    }

    list.querySelectorAll('.btn-generate-quiz').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget;
            const originalText = target.innerHTML;
            target.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            target.disabled = true;

            generateQuizAPI(task.task)
                .then(data => {
                    if (data.quiz && data.quiz.length > 0) {
                        task.quiz_data = data.quiz;
                        saveStateAPI();
                        openModuleView(qIndex, tIndex);
                    } else {
                        alert('Error generating quiz.');
                        target.innerHTML = originalText;
                        target.disabled = false;
                    }
                })
                .catch(err => {
                    alert('Connection error.');
                    target.innerHTML = originalText;
                    target.disabled = false;
                });
        });
    });

    list.querySelectorAll('.btn-submit-test').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const container = document.getElementById(`quiz-form-${qIndex}-${tIndex}`);
            const questions = container.querySelectorAll('.quiz-question');

            let correctCount = 0;
            let userAnswers = [];
            let allAnswered = true;

            questions.forEach((qDiv, idx) => {
                const selected = qDiv.querySelector(`input[name="q-${qIndex}-${tIndex}-${idx}"]:checked`);
                if (!selected) {
                    allAnswered = false;
                } else {
                    const selVal = parseInt(selected.value);
                    const correctVal = parseInt(qDiv.getAttribute('data-correct'));
                    userAnswers.push(selVal);
                    if (selVal === correctVal) correctCount++;
                }
            });

            if (!allAnswered) {
                alert('Please answer all questions before submitting.');
                return;
            }

            const percentage = Math.round((correctCount / questions.length) * 100);
            task.quiz_score = percentage;
            task.user_answers = userAnswers;

            saveStateAPI();
            openModuleView(qIndex, tIndex);
        });
    });

    list.querySelectorAll('.quiz-option-input:not([disabled])').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const groupName = e.target.name;
            document.querySelectorAll(`input[name="${groupName}"]`).forEach(r => {
                const lbl = document.querySelector(`label[for="${r.id}"]`);
                if (r.checked) {
                    lbl.classList.remove('bg-white', 'text-dark');
                    lbl.classList.add('bg-primary', 'text-white', 'border-primary');
                } else {
                    lbl.classList.remove('bg-primary', 'text-white', 'border-primary');
                    lbl.classList.add('bg-white', 'text-dark');
                }
            });
        });
    });

    list.querySelectorAll('.btn-new-test').forEach(btn => {
        btn.addEventListener('click', (e) => {
            delete task.quiz_data;
            delete task.quiz_score;
            delete task.user_answers;
            saveStateAPI();
            openModuleView(qIndex, tIndex);
        });
    });

    list.querySelectorAll('.btn-explain').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.currentTarget;
            const questionIdx = parseInt(target.getAttribute('data-questionidx'));
            const qData = task.quiz_data[questionIdx];
            const userAnswerText = qData.options[task.user_answers[questionIdx]];
            const correctAnswerText = qData.options[qData.correct_option_index];

            const explainBox = document.getElementById(`explain-box-${qIndex}-${tIndex}-${questionIdx}`);

            target.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            target.disabled = true;

            explainQuizAPI(qData.question, userAnswerText, correctAnswerText)
                .then(data => {
                    target.style.display = 'none';
                    explainBox.innerHTML = window.DOMPurify.sanitize(`<strong>ORIA:</strong> ${data.explanation}`);
                    explainBox.style.display = 'block';
                })
                .catch(err => {
                    alert('Error loading explanation.');
                    target.innerHTML = 'Explain Why';
                    target.disabled = false;
                });
        });
    });
    const modalEl = document.getElementById('questChainModal');
    if (window.bootstrap) {
        let modal = window.bootstrap.Modal.getInstance(modalEl);
        if (!modal) {
            modal = new window.bootstrap.Modal(modalEl);
        }
        if (!modalEl.classList.contains('show')) {
            modal.show();
        }
    }
}

export async function checkQuestCompletion(qIndex) {
    const quest = OriaState.quests[qIndex];
    if (!quest || quest.completed) return;

    let allDone = true;
    for (const t of quest.sub_tasks) {
        if (t.micro_steps && t.micro_steps.length > 0) {
            if (!t.micro_steps.every(m => m.completed)) {
                allDone = false;
                break;
            }
        } else {
            if (!t.completed) {
                allDone = false;
                break;
            }
        }
    }

    if (allDone) {
        quest.completed = true;
        const masterReward = quest.xp_reward || (quest.sub_tasks.length * 50);
        await addXP(masterReward);

        OriaAudio.playSuccess();
        showCyberToast('Quest Completed! 🎉', `You earned +${masterReward} XP`, 'success');

        const modalEl = document.getElementById('questChainModal');
        if (window.bootstrap && modalEl) {
            let modal = window.bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }
    }
}

export async function completeTask(qIndex, tIndex) {
    const task = OriaState.quests[qIndex].sub_tasks[tIndex];
    if (task && !task.completed) {
        OriaAudio.playSuccess();
        task.completed = true;
        await addXP(task.xp_reward || 50);

        await checkQuestCompletion(qIndex);

        try {
            await saveStateAPI();
        } catch (err) {
            console.error('Failed to save module completion', err);
        }

        renderQuests();
        renderProfileQuests();
    }
}

export function renderProfileQuests() {
    const container = document.getElementById('completed-quests-container');
    if (!container) return;

    const allQuests = OriaState.quests.map((q, idx) => ({ ...q, originalIndex: idx }));
    const completedQuests = allQuests.filter(q => q.sub_tasks && q.sub_tasks.length > 0 && q.sub_tasks.every(t => t.completed));

    if (completedQuests.length === 0) {
        container.innerHTML = `
            <div class="empty-state text-center p-5 mt-4" style="background: var(--card-bg-solid); border: 1px dashed var(--glass-border-solid); border-radius: var(--radius-lg);">
                <div class="mb-3" style="font-size: 2.5rem; color: var(--accent-blue); opacity: 0.5;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mb-2"><line x1="22" y1="12" x2="2" y2="12"></line><path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="6" y1="16" x2="6.01" y2="16"></line><line x1="10" y1="16" x2="10.01" y2="16"></line></svg>
                </div>
                <h6 class="fw-bold" style="color: var(--text-main);">No Records</h6>
                <p class="text-muted small mb-0 fw-semibold">No completed objectives found in the databanks.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = '';
    completedQuests.forEach(quest => {
        const completedTasks = quest.sub_tasks.filter(t => t.completed).length;
        const totalTasks = quest.sub_tasks.length;
        const progress = Math.round((completedTasks / totalTasks) * 100) || 0;

        const card = document.createElement('div');
        card.className = 'quest-card p-3 mb-2 shadow-sm rounded-3 border';
        card.style.cursor = 'pointer';
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="fw-bold mb-0 text-dark">${quest.title}</h6>
                <span class="badge" style="background: var(--accent-blue);">${window.t(quest.difficulty.toLowerCase()) || window.t(quest.difficulty) || quest.difficulty}</span>
            </div>
            <div class="progress mt-2 border" style="height: 6px; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);">
              <div class="progress-bar" role="progressbar" style="width: ${progress}%; background: var(--accent-blue);"></div>
            </div>
            <div class="d-flex justify-content-between mt-2 small text-muted">
                <span>${completedTasks}/${totalTasks} ${window.t('txt_tasks')}</span>
                <span class="fw-bold">${progress}%</span>
            </div>
        `;

        card.addEventListener('click', () => openQuestModal(quest.originalIndex));

        container.appendChild(card);
    });
}

export function updateGlobalMascot() {
    const equipped = OriaState.equipped_skin || "default";
    const currentSkin = storeItems.find(s => s.id === equipped);
    if (currentSkin) {
        document.querySelectorAll('.mascot-home').forEach(img => {
            img.src = currentSkin.image;
        });
    }
}

export function renderInventory() {
    const container = document.getElementById('inventory-grid');
    if (!container) return;

    container.innerHTML = '';
    const owned = OriaState.owned_skins || ["default"];
    const equipped = OriaState.equipped_skin || "default";

    updateGlobalMascot();

    const ownedItems = storeItems.filter(item => owned.includes(item.id));

    ownedItems.forEach(item => {
        const isEquipped = equipped === item.id;

        const card = document.createElement('div');
        card.className = `store-card ${isEquipped ? 'border-primary' : ''}`;
        if (isEquipped) card.style.borderWidth = '2px';

        let btnHtml = '';
        if (isEquipped) {
            btnHtml = `<button class="btn btn-sm btn-success w-100 rounded-pill fw-bold disabled">${window.t('txt_equipped')}</button>`;
        } else {
            btnHtml = `<button class="btn btn-sm btn-outline-primary w-100 rounded-pill fw-bold" onclick="window.equipSkin('${item.id}')">${window.t('btn_equip')}</button>`;
        }

        card.innerHTML = `
            <div class="store-card-img-wrapper" style="background: var(--gradient-card);">
               <img src="${item.image}" alt="${item.name}" class="store-card-img">
            </div>
            <div>
               <div class="store-card-title">${item.name}</div>
               ${btnHtml}
            </div>
        `;
        container.appendChild(card);
    });
}

let isSpinning = false;
export function spinRouletteHandler(cost) {
    if (isSpinning) return;

    // ── Lv3 gate (frontend) ────────────────────────────────────────────────
    if (OriaState.level < 3) {
        const msgEl = document.getElementById('roulette-msg');
        if (msgEl) {
            msgEl.textContent = '🔒 Roulette unlocks at Level 3!';
            msgEl.className = 'text-warning small mt-2 mb-0 fw-bold';
        }
        return;
    }

    if (OriaState.coins < cost) {
        alert('Not enough coins to spin!');
        return;
    }

    isSpinning = true;
    const msgEl = document.getElementById('roulette-msg');
    const imgEl = document.getElementById('roulette-display-img');
    const btnEl = document.getElementById('btn-spin-roulette');

    msgEl.textContent = window.t('spinning');
    msgEl.className = 'text-primary small mt-2 mb-0 fw-bold';
    btnEl.disabled = true;

    imgEl.style.filter = 'none';

    let spinCount = 0;
    const spinInterval = setInterval(() => {
        imgEl.src = storeItems[spinCount % storeItems.length].image;
        spinCount++;
    }, 50);

    spinRouletteAPI()
        .then(data => {
            setTimeout(() => {
                clearInterval(spinInterval);
                isSpinning = false;
                btnEl.disabled = false;

                if (data.success) {
                    OriaState.coins = data.coins;
                    OriaState.owned_skins.push(data.unlocked_skin);

                    if (data.newly_unlocked && data.newly_unlocked.length > 0) {
                        data.newly_unlocked.forEach(ach => {
                            if (!OriaState.achievements) OriaState.achievements = [];
                            if (!OriaState.achievements.includes(ach)) {
                                OriaState.achievements.push(ach);
                            }
                            showAchievementBanner(ach);
                        });
                    }

                    const wonSkinObj = storeItems.find(s => s.id === data.unlocked_skin);
                    if (wonSkinObj) imgEl.src = wonSkinObj.image;

                    msgEl.textContent = `${window.t('unlocked')} ${wonSkinObj ? wonSkinObj.name : data.unlocked_skin}! 🎉`;
                    msgEl.className = 'text-success small mt-2 mb-0 fw-bold';

                    updateDOMState();
                    updateGlobalMascot();
                    renderInventory();
                } else {
                    imgEl.src = '/static/img/IMG_8435.PNG';
                    imgEl.style.filter = 'brightness(0) invert(0.8)';
                    msgEl.textContent = data.error;
                    msgEl.className = 'text-danger small mt-2 mb-0 fw-bold';
                }
            }, 1000);
        })
        .catch(err => {
            clearInterval(spinInterval);
            isSpinning = false;
            btnEl.disabled = false;
            msgEl.textContent = 'Error connecting to system.';
            msgEl.className = 'text-danger small mt-2 mb-0 fw-bold';
            console.error(err);
        });
}

export function equipSkinHandler(id) {
    const previousSkin = OriaState.equipped_skin;
    OriaState.equipped_skin = id;
    updateGlobalMascot();
    renderInventory();

    equipSkinAPI(id)
        .then(data => {
            if (!data.success) {
                OriaState.equipped_skin = previousSkin;
                updateGlobalMascot();
                renderInventory();
                alert(data.error || 'Failed to equip skin');
            }
        })
        .catch(err => {
            OriaState.equipped_skin = previousSkin;
            updateGlobalMascot();
            renderInventory();
            console.error('Error equipping skin:', err);
        });
}

// Global scope attachments for inline HTML onClick handlers
window.spinRoulette = spinRouletteHandler;
window.refreshDailyQuests = refreshDailyQuestsHandler;
window.equipSkin = equipSkinHandler;

window.showDashboard = function (e) {
    if (e) e.preventDefault();
    document.getElementById('dashboard-view').classList.remove('d-none');
    document.getElementById('profile-view').classList.add('d-none');
    document.getElementById('stats-view').classList.add('d-none');
    document.getElementById('rewards-view').classList.add('d-none');
    document.getElementById('header-gamification-stats').classList.remove('d-none');
    document.getElementById('nav-btn-home').classList.add('active');
    document.getElementById('nav-btn-profile').classList.remove('active');
    document.getElementById('nav-btn-stats').classList.remove('active');
    document.getElementById('nav-btn-rewards').classList.remove('active');
};

export function showAchievementBanner(id) {
    const titles = {
        'initiate': { title: window.t('ach_initiate_title'), icon: '🔰', desc: window.t('ach_initiate_desc') },
        'on_fire': { title: window.t('ach_on_fire_title'), icon: '🔥', desc: window.t('ach_on_fire_desc') },
        'cyber_spender': { title: window.t('ach_spender_title'), icon: '💸', desc: window.t('btn_buy_skin') }
    };

    const ach = titles[id];
    if (!ach) return;

    const toast = document.getElementById('achievement-toast');
    if (!toast) return;

    document.getElementById('toast-icon').textContent = ach.icon;
    document.getElementById('toast-title').textContent = window.t('txt_achievement_unlocked') + ': ' + ach.title;
    document.getElementById('toast-desc').textContent = ach.desc;

    toast.classList.remove('toast-hidden');
    toast.classList.add('toast-visible');

    if (window.OriaAudio) {
        window.OriaAudio.playSuccess();
    }

    setTimeout(() => {
        toast.classList.remove('toast-visible');
        toast.classList.add('toast-hidden');
    }, 4000);
}

let productivityChartInstance = null;

function renderAnalyticsChart() {
    const canvas = document.getElementById('productivityChart');
    if (!canvas) return;

    // Count Categories
    const counts = {
        'Study & Exams': 0,
        'Project & Coding': 0,
        'Habits & Routine': 0,
        'General': 0
    };

    if (OriaState && OriaState.quests) {
        OriaState.quests.forEach(q => {
            const cat = q.category || 'General';
            if (counts[cat] !== undefined) {
                counts[cat]++;
            } else {
                counts['General']++;
            }
        });
    }

    const dataValues = [
        counts['Study & Exams'],
        counts['Project & Coding'],
        counts['Habits & Routine'],
        counts['General']
    ];

    // Destroy previous instance to prevent overlapping glitches
    if (productivityChartInstance) {
        productivityChartInstance.destroy();
    }

    const ctx = canvas.getContext('2d');
    productivityChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [window.t('cat_study'), window.t('cat_coding'), window.t('cat_habits'), window.t('cat_general')],
            datasets: [{
                data: dataValues,
                backgroundColor: [
                    '#00f0ff', // Cyan
                    '#ff003c', // Neon Pink
                    '#7000ff', // Purple
                    '#00ff66'  // Neon Green
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'var(--text-main)',
                        font: {
                            family: "'Outfit', sans-serif",
                            size: 11
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 18, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'var(--glass-border-solid)',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 8,
                    displayColors: true
                }
            }
        }
    });
}

window.showStats = function (e) {
    if (e) e.preventDefault();
    document.getElementById('dashboard-view').classList.add('d-none');
    document.getElementById('profile-view').classList.add('d-none');
    document.getElementById('stats-view').classList.remove('d-none');
    document.getElementById('rewards-view').classList.add('d-none');
    document.getElementById('header-gamification-stats').classList.add('d-none');
    document.getElementById('nav-btn-home').classList.remove('active');
    document.getElementById('nav-btn-profile').classList.remove('active');
    document.getElementById('nav-btn-stats').classList.add('active');
    document.getElementById('nav-btn-rewards').classList.remove('active');

    // Update Achievement Badges
    const badgeIds = {
        'initiate': 'badge-initiate',
        'on_fire': 'badge-on-fire',
        'cyber_spender': 'badge-cyber-spender'
    };

    for (const [achId, domId] of Object.entries(badgeIds)) {
        const el = document.getElementById(domId);
        if (!el) continue;

        if (OriaState && OriaState.achievements && OriaState.achievements.includes(achId)) {
            el.classList.remove('badge-locked');
            el.classList.add('badge-unlocked');
        } else {
            el.classList.remove('badge-unlocked');
            el.classList.add('badge-locked');
        }
    }

    renderAnalyticsChart();
    renderLeaderboard();
};

async function renderLeaderboard() {
    const listContainer = document.getElementById('leaderboard-list-container');
    if (!listContainer) return;

    listContainer.innerHTML = `<div class="text-center p-3"><small class="text-muted">${window.t('txt_loading_hackers')}</small></div>`;

    try {
        const data = await fetchLeaderboardAPI();
        if (data.leaderboard) {
            listContainer.innerHTML = '';
            data.leaderboard.forEach((user, index) => {
                const isCurrentUser = user.is_current_user;
                const rowBlock = document.createElement('div');

                // Add specific styling for current user
                if (isCurrentUser) {
                    rowBlock.className = 'list-group-item d-flex justify-content-between align-items-center p-3 current-user-row';
                    rowBlock.style.background = 'rgba(137, 175, 240, 0.1)';
                    rowBlock.style.borderBottom = '1px solid var(--glass-border-solid)';
                } else {
                    rowBlock.className = 'list-group-item d-flex justify-content-between align-items-center p-3 other-user-row';
                    rowBlock.style.background = 'transparent';
                    rowBlock.style.borderBottom = '1px solid var(--glass-border-solid)';
                }

                const rankClass = index === 0 ? 'text-warning' : (index === 1 ? 'text-secondary' : (index === 2 ? 'text-success' : 'text-muted'));
                const nameClass = isCurrentUser ? 'text-primary' : 'text-main';
                // Use the title the user has explicitly equipped (from backend)
                const title = user.equipped_title || '';
                const titleHtml = title
                    ? `<span class="badge rounded-pill ms-1 fw-bold" style="background: var(--primary-gradient); font-size: 0.7rem;">${title}</span>`
                    : '';

                rowBlock.innerHTML = `
                    <div class="d-flex align-items-center gap-3">
                        <span class="fs-4 fw-bold ${rankClass}">${index + 1}</span>
                        <div>
                            <h6 class="mb-0 fw-bold ${nameClass} d-flex align-items-center gap-1">${user.username}${isCurrentUser ? ` ${window.t('txt_you')}` : ''} ${title ? `<span class="badge rounded-pill fw-bold leaderboard-title-badge ${isCurrentUser ? 'leaderboard-current-user-title' : ''}" style="background: var(--primary-gradient); font-size: 0.68rem; vertical-align: middle;">${title}</span>` : (isCurrentUser ? `<span class="leaderboard-current-user-title" style="display:none;"></span>` : '')}</h6>
                            <small class="${isCurrentUser ? 'text-primary' : 'text-muted'}">Lvl ${user.level} • ${user.xp} XP •  🔥 ${user.current_streak || 0} ${window.t('txt_days')}</small>
                        </div>
                    </div>
                `;
                listContainer.appendChild(rowBlock);
            });
        }
    } catch (err) {
        listContainer.innerHTML = `<div class="text-center p-3 text-danger"><small>${window.t('txt_failed_leaderboard')}</small></div>`;
        console.error("Leaderboard Error:", err);
    }
}

window.showProfile = function (e) {
    if (e) e.preventDefault();
    document.getElementById('dashboard-view').classList.add('d-none');
    document.getElementById('stats-view').classList.add('d-none');
    document.getElementById('rewards-view').classList.add('d-none');
    document.getElementById('profile-view').classList.remove('d-none');
    document.getElementById('header-gamification-stats').classList.add('d-none');
    document.getElementById('nav-btn-home').classList.remove('active');
    document.getElementById('nav-btn-stats').classList.remove('active');
    document.getElementById('nav-btn-rewards').classList.remove('active');
    document.getElementById('nav-btn-profile').classList.add('active');

    // ── Equipped title badge (manual, not auto-calculated) ──────────────────
    const titleBadge = document.getElementById('profile-title-badge');
    if (titleBadge) {
        const eq = OriaState.equipped_title || '';
        if (eq) {
            titleBadge.textContent = eq;
            titleBadge.style.display = 'inline-block';
        } else {
            titleBadge.style.display = 'none';
        }
    }

    // ── Title select dropdown (only includes claimed titles) ──────────────
    const titleSelectContainer = document.getElementById('title-select-container');
    if (titleSelectContainer) {
        const titleRewards = { 5: 'Cyber Initiate', 10: 'Neural Hacker', 20: 'System Overlord' };
        const claimed = OriaState.claimed_rewards || [1];
        const unlockedTitles = Object.entries(titleRewards)
            .filter(([lvl]) => claimed.includes(parseInt(lvl)))
            .map(([, title]) => title);

        if (unlockedTitles.length === 0) {
            titleSelectContainer.innerHTML = `
                <p class="fw-bold mb-1" style="background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 0.8rem; letter-spacing: 0.08em;">${window.t('txt_equipped_title')}</p>
                <p class="text-muted small mb-0">
                    ${window.t('txt_no_titles_earned')}
                </p>`;
        } else {
            const current = OriaState.equipped_title || '';
            const options = [`<option value="">${window.t('no_title')}</option>`]
                .concat(unlockedTitles.map(t =>
                    `<option value="${t}"${t === current ? ' selected' : ''}>${t}</option>`
                )).join('');

            titleSelectContainer.innerHTML = `
                <p class="fw-bold mb-2" style="background: var(--primary-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 0.8rem; letter-spacing: 0.08em;">${window.t('txt_equipped_title')}</p>
                <select id="equipped-title-select" class="form-select form-select-sm title-select-themed">
                    ${options}
                </select>`;

            document.getElementById('equipped-title-select').addEventListener('change', async function () {
                const newTitle = this.value;
                OriaState.equipped_title = newTitle;

                // 1. Update profile badge instantly
                if (titleBadge) {
                    if (newTitle) {
                        titleBadge.textContent = newTitle;
                        titleBadge.style.display = 'inline-block';
                    } else {
                        titleBadge.style.display = 'none';
                    }
                }

                // 2. Persist to backend
                try {
                    await saveStateAPI();
                } catch (err) {
                    console.error('Title save failed:', err);
                }

                // 3. If the stats/leaderboard view is visible, re-render it immediately
                const statsView = document.getElementById('stats-view');
                if (statsView && !statsView.classList.contains('d-none')) {
                    // fetchLeaderboardAPI returns server data which now has the new equipped_title
                    // But we can do an optimistic local update too:
                    document.querySelectorAll('.leaderboard-current-user-title').forEach(el => {
                        el.textContent = newTitle || '';
                    });
                }
            });
        }
    }

    // ── Lv3 roulette gate (frontend visual) ────────────────────────────────
    const rouletteArea = document.getElementById('roulette-area');
    const spinBtn = document.getElementById('btn-spin-roulette');
    const rouletteMsg = document.getElementById('roulette-msg');
    if (rouletteArea && spinBtn) {
        if (OriaState.level < 3) {
            rouletteArea.classList.add('roulette-locked-overlay');
            spinBtn.textContent = '🔒 Unlocks at Lv. 3';
            spinBtn.classList.add('btn-secondary');
            spinBtn.classList.remove('btn-primary');
            if (rouletteMsg) {
                rouletteMsg.textContent = `Reach Level 3 to unlock Skin Roulette. (Current: Lv. ${OriaState.level})`;
                rouletteMsg.className = 'text-warning small mt-2 mb-0 fw-bold';
            }
        } else {
            rouletteArea.classList.remove('roulette-locked-overlay');
            if (spinBtn.textContent.includes('Unlocks')) {
                spinBtn.innerHTML = `SPIN (<img src="/static/img/star-icon.svg" width="18" height="18" alt="Star" style="vertical-align: middle; margin-top: -3px;"> 100)`;
            }
            spinBtn.classList.remove('btn-secondary');
            spinBtn.classList.add('btn-primary');
            if (rouletteMsg && rouletteMsg.textContent.includes('Reach')) {
                rouletteMsg.textContent = '';
            }
        }
    }
};

window.showRewards = function (e) {
    if (e) e.preventDefault();
    document.getElementById('dashboard-view').classList.add('d-none');
    document.getElementById('profile-view').classList.add('d-none');
    document.getElementById('stats-view').classList.add('d-none');
    document.getElementById('rewards-view').classList.remove('d-none');
    document.getElementById('header-gamification-stats').classList.add('d-none');
    document.getElementById('nav-btn-home').classList.remove('active');
    document.getElementById('nav-btn-stats').classList.remove('active');
    document.getElementById('nav-btn-profile').classList.remove('active');
    document.getElementById('nav-btn-rewards').classList.add('active');

    const rewardsLevelEl = document.getElementById('rewards-current-level');
    if (rewardsLevelEl) rewardsLevelEl.textContent = OriaState.level;

    const claimed = OriaState.claimed_rewards || [1];

    // Render status column for each row
    document.querySelectorAll('.rewards-status').forEach(cell => {
        const requiredLevel = parseInt(cell.getAttribute('data-level'), 10);
        cell.innerHTML = '';

        if (claimed.includes(requiredLevel)) {
            // Already claimed
            cell.innerHTML = `<span class="fw-bold" style="color: var(--bs-success);">\u2713 ${window.t('claimed')}</span>`;
        } else if (OriaState.level >= requiredLevel) {
            // Eligible — show Claim button
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-primary fw-bold rounded-pill px-3';
            btn.textContent = window.t('claim');
            btn.dataset.level = requiredLevel;
            btn.addEventListener('click', async function () {
                btn.disabled = true;
                btn.textContent = '...';
                try {
                    const data = await claimRewardAPI(requiredLevel);
                    // Sync coins from server
                    OriaState.coins = data.coins;
                    OriaState.claimed_rewards = data.claimed_rewards;
                    updateDOMState();
                    // Re-render all status cells and refresh title select
                    window.showRewards();
                    // If profile is not showing, still refresh select next time it opens
                } catch (err) {
                    btn.disabled = false;
                    btn.textContent = window.t('claim');
                    const msg = err.message || 'Claim failed';
                    cell.innerHTML += `<br><small class="text-danger">${msg}</small>`;
                }
            });
            cell.appendChild(btn);
        } else {
            // Locked
            cell.innerHTML = `<span class="badge" style="background: rgba(128,128,128,0.2); color: var(--text-muted);">${window.t('level_needed', { L: requiredLevel })}</span>`;
        }
    });
};

window.addEventListener('achievementUnlocked', (e) => {
    if (e.detail && e.detail.id) {
        showAchievementBanner(e.detail.id);
    }
});

export function showCyberToast(title, message, type = 'success') {
    const toast = document.createElement('div');

    // Determine the glowing border color based on the type
    let borderColor = 'var(--accent-blue)';
    if (type === 'success') borderColor = 'var(--accent-green, #20c997)';
    if (type === 'warning' || type === 'error') borderColor = 'var(--accent-pink, #ff2a6d)';

    // Style the toast matching the cyberpunk visual theme
    toast.className = 'glass-card shadow-lg p-3 d-flex align-items-center mb-3 mb-sm-4 me-sm-2';
    toast.style.position = 'fixed';
    toast.style.top = '25px';
    toast.style.right = '25px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '280px';
    toast.style.borderRadius = '12px';
    toast.style.border = `1px solid ${borderColor}`;
    toast.style.borderLeft = `5px solid ${borderColor}`;
    toast.style.background = 'var(--card-bg)';
    toast.style.color = 'var(--text-main)';
    toast.style.transform = 'translateX(120%)';
    toast.style.transition = 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.4s ease';
    toast.style.opacity = '0';

    // Icon logic based on success or warning
    const iconHtml = type === 'success'
        ? `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${borderColor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="me-3"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`
        : `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="${borderColor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="me-3"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;

    // Build the inner HTML
    toast.innerHTML = `
        ${iconHtml}
        <div>
            <h6 class="fw-bold mb-1" style="font-size: 1rem;">${title}</h6>
            <p class="mb-0 small" style="color: var(--text-muted);">${message}</p>
        </div>
    `;

    document.body.appendChild(toast);

    // Trigger animation (slide in)
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);

    // Remove after 3.5 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 400); // Wait for transition finish
    }, 3500);
}
