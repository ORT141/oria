import { OriaState, setState, initTheme, toggleTheme } from './state.js';
import { fetchUserState, fetchChatHistoryAPI, sendChatMessageAPI, saveStateAPI } from './api.js';
import {
    OriaMascot, updateDOMState, renderQuests, renderDailyQuests,
    renderProfileQuests, updateGlobalMascot, renderInventory
} from './ui.js';

// Instantly apply theme to prevent white flashing
initTheme();

console.log('ORIA initialized via ES Modules');

document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle Listener
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const newTheme = toggleTheme();
            const icon = themeBtn.querySelector('svg');
            if (newTheme === 'dark') {
                icon.classList.remove('bi-moon-fill');
                icon.classList.add('bi-sun-fill');
                icon.innerHTML = '<path d="M8 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm0 1a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z"/>';
            } else {
                icon.classList.remove('bi-sun-fill');
                icon.classList.add('bi-moon-fill');
                icon.innerHTML = '<path d="M6 .278a.77.77 0 0 1 .08.858 7.2 7.2 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277q.792-.001 1.533-.16a.79.79 0 0 1 .81.316.73.73 0 0 1-.031.893A8.35 8.35 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.75.75 0 0 1 6 .278"/>';
            }
        });

        // Set initial icon if dark mode loaded
        if (document.documentElement.getAttribute('data-theme') === 'dark') {
            const icon = themeBtn.querySelector('svg');
            icon.classList.remove('bi-moon-fill');
            icon.classList.add('bi-sun-fill');
            icon.innerHTML = '<path d="M8 11a3 3 0 1 1 0-6 3 3 0 0 1 0 6zm0 1a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z"/>';
        }
    }
    // 1. Initialize Mascot
    const mascotImg = document.querySelector('.mascot-home, .mascot-register');
    if (mascotImg) {
        mascotImg.id = 'oria-mascot';
        new OriaMascot('oria-mascot', {
            default: '/static/img/IMG_8442.PNG',
            blinking: '/static/img/IMG_8435.PNG',
            talking: '/static/img/IMG_8441.PNG'
        });
    }

    // 2. Load History & Gamification State
    fetchUserState().then(data => {
        if (!data.error) {
            setState(data);
            updateDOMState();
            renderQuests();
            renderDailyQuests();
            renderInventory();
            renderProfileQuests();
            loadChatHistory();
        }
    });

    // 3. Chat Initialization
    const chatInput = document.getElementById('chat-input-text');
    const btnSend = document.getElementById('btn-send-chat');
    const messagesContainer = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('chat-typing');

    function loadChatHistory() {
        if (!messagesContainer) return;

        fetchChatHistoryAPI()
            .then(data => {
                if (data.history && data.history.length > 0) {
                    messagesContainer.innerHTML = '';
                    data.history.forEach(msg => {
                        const isUser = msg.role === 'user';
                        appendChatDOM(msg.content, isUser);
                    });
                }
            })
            .catch(err => console.error("Error loading chat:", err));
    }

    function appendChatDOM(text, isUser) {
        if (!messagesContainer) return;
        const div = document.createElement('div');
        div.className = `chat-bubble p-3 shadow-sm ${isUser ? 'user ms-auto text-white' : 'ai'}`;

        if (isUser) {
            div.style.background = 'var(--primary-gradient)';
            div.style.borderBottomRightRadius = '4px';
            div.style.maxWidth = '85%';
            div.textContent = text;
        } else {
            div.style.background = 'white';
            div.style.borderBottomLeftRadius = '4px';
            div.style.maxWidth = '85%';
            if (window.marked && window.marked.parse) {
                div.innerHTML = window.DOMPurify.sanitize(window.marked.parse(text));
            } else {
                div.innerHTML = window.DOMPurify.sanitize(text.replace(/\n/g, '<br>'));
            }
        }
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function sendChatMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        appendChatDOM(text, true);
        chatInput.value = '';
        typingIndicator.classList.remove('d-none');

        sendChatMessageAPI(text, false)
            .then(data => {
                typingIndicator.classList.add('d-none');
                if (data.reply) {
                    appendChatDOM(data.reply, false);
                    if (data.quest_added && data.quest) {
                        OriaState.quests.push(data.quest);
                        renderQuests();
                        appendChatDOM(`SYSTEM ALERT: Saved new quest "${data.quest.title}" to your active quests!`, false);
                    }
                } else {
                    appendChatDOM("Error communicating with Neural Link.", false);
                }
            })
            .catch(err => {
                typingIndicator.classList.add('d-none');
                appendChatDOM("Connection lost. Neural link severed.", false);
            });
    }

    if (btnSend) btnSend.addEventListener('click', sendChatMessage);
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    // 4. Quick Quest Logic
    const qqInput = document.getElementById('quick-quest-input');
    const qqBtn = document.getElementById('btn-quick-quest');

    function generateQuickQuest() {
        const goal = qqInput.value.trim();
        if (!goal) {
            alert("Please enter a short goal to generate a quest!");
            return;
        }

        const originalText = qqBtn.innerText;
        qqBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        qqBtn.disabled = true;

        sendChatMessageAPI(goal, true)
            .then(data => {
                qqBtn.innerHTML = originalText;
                qqBtn.disabled = false;
                qqInput.value = '';

                if (data.quest) {
                    OriaState.quests.push(data.quest);
                    saveStateAPI();
                    renderQuests();
                } else {
                    alert('Failed to generate quest from neural link.');
                }
            })
            .catch(err => {
                qqBtn.innerHTML = originalText;
                qqBtn.disabled = false;
                alert('Error generating quest. Re-establishing link...');
            });
    }

    if (qqBtn) qqBtn.addEventListener('click', generateQuickQuest);
    if (qqInput) {
        qqInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') generateQuickQuest();
        });
    }
});
