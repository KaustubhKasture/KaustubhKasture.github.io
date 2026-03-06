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

    sendButton.addEventListener('click', () => {
        const messageText = chatInput.value;
        if (messageText.trim() !== '') {
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
            botMessage.textContent = 'Personalised LLM in development...';
            chatMessages.appendChild(botMessage);

            chatInput.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
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
});