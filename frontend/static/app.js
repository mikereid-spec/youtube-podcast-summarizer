let currentSessionId = null;

// Handle Enter key for inputs
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('youtube-url').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') summarizeVideo();
    });

    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});

async function summarizeVideo() {
    const urlInput = document.getElementById('youtube-url');
    const url = urlInput.value.trim();

    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }

    // Reset UI
    hideError();
    showLoading();
    hideElement('summary-section');
    hideElement('chat-section');
    document.getElementById('chat-messages').innerHTML = '';

    const btn = document.getElementById('summarize-btn');
    btn.disabled = true;

    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ youtube_url: url }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to summarize video');
        }

        const data = await response.json();
        currentSessionId = data.session_id;

        // Display summary
        displaySummary(data.summary, data.video_metadata);

        // Show chat section
        showElement('chat-section');
        document.getElementById('chat-input').focus();

    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
        btn.disabled = false;
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message || !currentSessionId) return;

    // Add user message to chat
    addMessage('user', message);
    input.value = '';

    const btn = document.getElementById('send-btn');
    btn.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get response');
        }

        const data = await response.json();
        addMessage('assistant', data.response);

    } catch (error) {
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        btn.disabled = false;
        input.focus();
    }
}

function displaySummary(summary, metadata) {
    const summaryContent = document.getElementById('summary-content');
    const metadataDiv = document.getElementById('video-metadata');

    // Convert markdown-style formatting to HTML
    const formattedSummary = formatMarkdown(summary);
    summaryContent.innerHTML = formattedSummary;

    // Display metadata
    const durationMinutes = Math.floor(metadata.duration_seconds / 60);
    metadataDiv.innerHTML = `
        <span>Duration: ${durationMinutes} minutes</span>
        <span>Segments: ${metadata.segment_count}</span>
        <span>Video ID: ${metadata.video_id}</span>
    `;

    showElement('summary-section');
}

function addMessage(role, content) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const label = role === 'user' ? 'You' : 'Assistant';
    messageDiv.innerHTML = `
        <div class="message-label">${label}</div>
        <div class="message-content">${formatMarkdown(content)}</div>
    `;

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function formatMarkdown(text) {
    // Basic markdown formatting
    return text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/### (.+)/g, '<h3>$1</h3>')
        .replace(/## (.+)/g, '<h2>$1</h2>')
        .replace(/# (.+)/g, '<h1>$1</h1>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n- /g, '<br>• ');
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function hideError() {
    document.getElementById('error').classList.add('hidden');
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function showElement(id) {
    document.getElementById(id).classList.remove('hidden');
}

function hideElement(id) {
    document.getElementById(id).classList.add('hidden');
}
