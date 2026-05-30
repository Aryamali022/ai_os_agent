const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const welcomeMessage = document.querySelector('.welcome-message');

// Always point to the FastAPI backend (works from Live Server or any other host)
const API_BASE = 'http://127.0.0.1:8000';

function sendSuggestion(text) {
    messageInput.value = text;
    messageInput.focus();
    document.getElementById('chatForm').dispatchEvent(new Event('submit'));
}

async function handleSubmit(event) {
    event.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;

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
                actionSpan.textContent = task.action.replace('_', ' ');

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
