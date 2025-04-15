document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');


    chatInput.addEventListener('focus', () => {
        chatInput.placeholder = '';
    });

    chatInput.addEventListener('blur', () => {
        if (chatInput.value === '') {
            chatInput.placeholder = 'Ask questions about Kaustubh';
        }
    });

    const chatMessages = document.querySelector('.chat-messages');
    const chatBoxContainer = document.querySelector('.chat-box-container');
    let isExpanded = false; 

    sendButton.addEventListener('click', () => {
        const messageText = chatInput.value;
        if (messageText.trim() !== '') {
            if (!isExpanded) {
                chatBoxContainer.classList.add('expanded');
                chatMessages.classList.add('expanded');
                isExpanded = true;
            }

            // User message
            const userMessage = document.createElement('div');
            userMessage.classList.add('user-message');
            userMessage.textContent = messageText;
            chatMessages.appendChild(userMessage);

            // Bot message
            const botMessage = document.createElement('div');
            botMessage.classList.add('bot-message');
            botMessage.textContent = 'Personalised LLM in development...';
            chatMessages.appendChild(botMessage);

            chatInput.value = '';

            chatMessages.scrollTop = chatMessages.scrollHeight;

            sendButton.classList.add('translucent');
            setTimeout(() => {
                sendButton.classList.remove('translucent');
            }, 300);
        }
    });

    chatInput.addEventListener('keypress', (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
            sendButton.click();
        }
    });

    document.addEventListener('click', (event) => {
        if (!chatBoxContainer.contains(event.target) && event.target !== chatInput && isExpanded) {
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
        if (event.keyCode === 27 && isExpanded) {
            chatBoxContainer.classList.remove('expanded');
            chatMessages.classList.remove('expanded');
            isExpanded = false;
            chatInput.blur();
        }
    });

    const aboutLink = document.getElementById('about-link');
    const aboutMeText = document.getElementById('about-me-text');
    const aboutMeParagraph = aboutMeText.querySelector('p');
    const aboutMeTextContent = aboutMeParagraph.textContent;
    aboutMeParagraph.textContent = '';
    let isAboutMeVisible = false;
    let typingInterval;

    aboutLink.addEventListener('click', (event) => {
        event.preventDefault();
        aboutMeText.style.display = 'none';

        if (isAboutMeVisible) {
            aboutMeText.style.display = 'none';
            isAboutMeVisible = false;
            clearInterval(typingInterval);
        } else {
            aboutMeText.style.display = 'block';
            isAboutMeVisible = true;

            aboutMeParagraph.textContent = '';
            let i = 0;
            typingInterval = setInterval(() => {
                if (i < aboutMeTextContent.length) {
                    aboutMeParagraph.textContent += aboutMeTextContent.charAt(i);
                    i++;
                } else {
                    clearInterval(typingInterval);
                }
            }, 20);
        }
    });
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