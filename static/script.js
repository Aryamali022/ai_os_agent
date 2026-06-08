const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const welcomeMessage = document.querySelector('.welcome-message');

// Always point to the FastAPI backend (works from Live Server or any other host)
const API_BASE = "http://127.0.0.1:5000";

function sendSuggestion(text) {
    messageInput.value = text;
    messageInput.focus();
    document.getElementById('sendBtn').click();
}

async function handleSubmit(event) {
    event.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;

    // Cancel any ongoing text-to-speech when a new message is submitted
    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        const mic = document.getElementById('micBtn');
        if (mic) mic.classList.remove('speaking');
    }

    // Cancel any ongoing speech recognition
    if (isListening && typeof stopListening === 'function') {
        stopListening();
    }

    // Remove welcome message if it exists
    if (welcomeMessage && welcomeMessage.parentNode) {
        welcomeMessage.parentNode.removeChild(welcomeMessage);
    }

    // Disable input while processing
    messageInput.value = '';
    messageInput.disabled = true;
    sendBtn.disabled = true;

    // Append User Message
    appendMessage('user', text);

    // Show Typing Indicator
    const typingId = showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => null);
            throw new Error(errData ? errData.detail : `Server returned HTTP ${response.status}`);
        }

        const data = await response.json();

        // Remove typing indicator
        removeElement(typingId);

        // Append Bot Message
        appendBotResponse(data);

        // Read response aloud if TTS is enabled
        if (typeof ttsEnabled !== 'undefined' && ttsEnabled) {
            speakText(data.response);
        }
    } catch (error) {
        console.error('Error:', error);
        removeElement(typingId);
        appendMessage('bot', `⚠️ ${error.message}`);
    } finally {
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

function appendMessage(sender, text) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${sender}`;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = text;

    const metaDiv = document.createElement('div');
    metaDiv.className = 'message-meta';
    metaDiv.textContent = sender === 'user' ? 'You' : 'AI OS Agent';

    wrapper.appendChild(messageDiv);
    wrapper.appendChild(metaDiv);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

function appendBotResponse(data) {
    const wrapper = document.createElement('div');
    wrapper.className = 'message-wrapper bot';

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';

    // Response text
    const textP = document.createElement('p');
    textP.textContent = data.response;
    messageDiv.appendChild(textP);

    // Render task results (skip GENERAL since those are just chat)
    if (data.tasks && data.tasks.length > 0) {
        const tasksContainer = document.createElement('div');
        tasksContainer.className = 'tasks-container';

        data.tasks.forEach(task => {
            if (task.action !== 'GENERAL') {
                const taskItem = document.createElement('div');
                taskItem.className = 'task-item';

                const header = document.createElement('div');
                header.className = 'task-header';

                const actionSpan = document.createElement('span');
                actionSpan.className = 'task-action';
                actionSpan.textContent = task.action.replace(/_/g, ' ');

                const paramSpan = document.createElement('span');
                paramSpan.className = 'task-params';
                paramSpan.textContent = task.parameters || '—';

                header.appendChild(actionSpan);
                header.appendChild(paramSpan);
                taskItem.appendChild(header);

                if (task.action_result) {
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'task-result';
                    resultDiv.textContent = task.action_result;
                    taskItem.appendChild(resultDiv);
                }

                tasksContainer.appendChild(taskItem);
            }
        });

        if (tasksContainer.childNodes.length > 0) {
            messageDiv.appendChild(tasksContainer);
        }
    }

    const metaDiv = document.createElement('div');
    metaDiv.className = 'message-meta';
    metaDiv.textContent = 'AI OS Agent';

    wrapper.appendChild(messageDiv);
    wrapper.appendChild(metaDiv);
    chatMessages.appendChild(wrapper);
    scrollToBottom();
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const indicator = document.createElement('div');
    indicator.id = id;
    indicator.className = 'typing-indicator';

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        indicator.appendChild(dot);
    }

    chatMessages.appendChild(indicator);
    scrollToBottom();
    return id;
}

function removeElement(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==========================================
// VOICE COMMAND SYSTEM INTEGRATION
// ==========================================

const micBtn = document.getElementById('micBtn');
const ttsToggle = document.getElementById('ttsToggle');
const autoSendToggle = document.getElementById('autoSendToggle');

let recognition = null;
let isListening = false;
let ttsEnabled = false;
let autoSendEnabled = true;
let currentUtterance = null;

// Initialize Speech Recognition
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    console.warn('Speech Recognition not supported in this browser.');
    if (micBtn) {
        micBtn.classList.add('disabled');
        micBtn.title = 'Speech recognition not supported in this browser';
    }
} else {
    recognition = new SpeechRecognition();
    recognition.continuous = false; // Stop when the user stops speaking
    recognition.interimResults = true; // Show results as they are transcribed
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isListening = true;
        micBtn.classList.add('listening');
        micBtn.title = 'Listening... Click to stop';
        messageInput.placeholder = 'Listening...';

        // Stop any text-to-speech if listening starts
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
            micBtn.classList.remove('speaking');
        }
    };

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join('');

        messageInput.value = transcript;
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        stopListening();
    };

    recognition.onend = () => {
        const hasText = messageInput.value.trim().length > 0;
        stopListening();

        // Auto-submit if enabled and we got some text input
        if (autoSendEnabled && hasText) {
            document.getElementById('sendBtn').click();
        }
    };
}

// Toggle functions
function startListening() {
    if (!recognition) return;
    try {
        recognition.start();
    } catch (e) {
        console.error('Failed to start recognition:', e);
    }
}

// Stop function
function stopListening() {
    isListening = false;
    if (micBtn) {
        micBtn.classList.remove('listening');
        micBtn.title = 'Click to speak';
    }
    if (messageInput) {
        messageInput.placeholder = 'Type your command...';
    }
    if (recognition) {
        try {
            recognition.stop();
        } catch (e) { }
    }
}

// Text to Speech
function speakText(text) {
    if (!window.speechSynthesis) return;

    // Cancel active speaking
    window.speechSynthesis.cancel();
    micBtn.classList.remove('speaking');

    // Strip emoji and private-use unicode so TTS doesn't read garbage characters
    let cleanText = text.replace(/[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2600-\u26FF]|\uD83E[\uDD00-\uDDFF]/g, '');

    if (!cleanText.trim()) return;

    currentUtterance = new SpeechSynthesisUtterance(cleanText);

    currentUtterance.onstart = () => {
        micBtn.classList.add('speaking');
        micBtn.title = 'Speaking response... Click to stop';
    };

    currentUtterance.onend = () => {
        micBtn.classList.remove('speaking');
        micBtn.title = 'Click to speak';
    };

    currentUtterance.onerror = () => {
        micBtn.classList.remove('speaking');
        micBtn.title = 'Click to speak';
    };

    window.speechSynthesis.speak(currentUtterance);
}

// Initialize Voice Settings
if (ttsToggle && autoSendToggle) {
    // Restore states from localStorage
    if (localStorage.getItem('ttsEnabled') === 'true') {
        ttsEnabled = true;
        ttsToggle.checked = true;
    } else {
        ttsEnabled = false;
        ttsToggle.checked = false;
    }

    if (localStorage.getItem('autoSendEnabled') === 'false') {
        autoSendEnabled = false;
        autoSendToggle.checked = false;
    } else {
        autoSendEnabled = true;
        autoSendToggle.checked = true;
    }

    // Settings event listeners
    ttsToggle.addEventListener('change', (e) => {
        ttsEnabled = e.target.checked;
        localStorage.setItem('ttsEnabled', ttsEnabled);
        if (!ttsEnabled && window.speechSynthesis) {
            window.speechSynthesis.cancel();
            micBtn.classList.remove('speaking');
            micBtn.title = 'Click to speak';
        }
    });

    autoSendToggle.addEventListener('change', (e) => {
        autoSendEnabled = e.target.checked;
        localStorage.setItem('autoSendEnabled', autoSendEnabled);
    });
}

// Mic button event listener
if (micBtn) {
    micBtn.addEventListener('click', () => {
        if (isListening) {
            stopListening();
        } else if (micBtn.classList.contains('speaking')) {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
            micBtn.classList.remove('speaking');
            micBtn.title = 'Click to speak';
        } else {
            startListening();
        }
    });
}

// Cancel speaking if user starts typing in message input
if (messageInput) {
    messageInput.addEventListener('input', () => {
        if (window.speechSynthesis && window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            if (micBtn) {
                micBtn.classList.remove('speaking');
                micBtn.title = 'Click to speak';
            }
        }
    });
}
