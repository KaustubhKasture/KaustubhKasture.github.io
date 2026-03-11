document.addEventListener('DOMContentLoaded', () => {
    const heroTime = document.getElementById('hero-time');
    function updateTime() {
        const now = new Date().toLocaleTimeString('en-IN', {
            timeZone: 'Asia/Kolkata',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
        heroTime.textContent = now + ' IST';
    }
    updateTime();
    setInterval(updateTime, 1000);

    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.querySelector('.chat-messages');
    const chatBoxContainer = document.querySelector('.chat-box-container');
    let isExpanded = false;

    chatInput.addEventListener('focus', () => {
        chatInput.placeholder = '';
    });

    chatInput.addEventListener('blur', () => {
        if (chatInput.value === '') {
            chatInput.placeholder = 'Ask questions about me and my work...';
        }
    });

    sendButton.addEventListener('click', async () => {
        const messageText = chatInput.value.trim();
        if (messageText === '') return;

        if (!isExpanded) {
            chatBoxContainer.classList.add('expanded');
            chatMessages.classList.add('expanded');
            isExpanded = true;
        }

        const userMessage = document.createElement('div');
        userMessage.classList.add('user-message');
        userMessage.textContent = messageText;
        chatMessages.appendChild(userMessage);

        const botMessage = document.createElement('div');
        botMessage.classList.add('bot-message');
        botMessage.textContent = '...';
        chatMessages.appendChild(botMessage);

        chatInput.value = '';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            botMessage.textContent = data.response || 'No response received.';
        } catch (error) {
            botMessage.textContent = 'Error: could not reach the chatbot.';
            console.error('Fetch error:', error);
        }

        chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendButton.click();
        }
    });

    document.addEventListener('click', (event) => {
        if (!chatBoxContainer.contains(event.target) && isExpanded) {
            chatBoxContainer.classList.remove('expanded');
            chatMessages.classList.remove('expanded');
            isExpanded = false;
            chatInput.blur();
        }
    });

    chatInput.addEventListener('focus', () => {
        if (!isExpanded && chatMessages.children.length > 0) {
            chatBoxContainer.classList.add('expanded');
            chatMessages.classList.add('expanded');
            isExpanded = true;
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && isExpanded) {
            chatBoxContainer.classList.remove('expanded');
            chatMessages.classList.remove('expanded');
            isExpanded = false;
            chatInput.blur();
        }
    });

    const articlesLink = document.getElementById('articles-link');
    const tooltip = document.getElementById('articles-tooltip');

    articlesLink.addEventListener('click', (e) => {
        e.preventDefault();
        tooltip.style.display = 'block';
        setTimeout(() => {
            tooltip.style.display = 'none';
        }, 2000);
    });

    // Project card default click → open data-default URL
    document.querySelectorAll('.project-card[data-default]').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.closest('.project-icon-btn')) return;
            window.open(card.dataset.default, '_blank', 'noopener,noreferrer');
        });
    });

    // Prevent disabled icon buttons from doing anything
    document.querySelectorAll('.project-icon-btn.disabled').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });

    // Stop icon link clicks from also triggering card click
    document.querySelectorAll('.project-icon-btn:not(.disabled)').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
        });
    });
});