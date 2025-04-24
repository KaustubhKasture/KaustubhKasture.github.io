document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.querySelector('.chat-messages');
    const chatBoxContainer = document.querySelector('.chat-box-container');
    let isExpanded = false; 
    let disclaimerAdded = false; // Track if disclaimer has been added to DOM

    chatInput.addEventListener('focus', () => {
        chatInput.placeholder = '';
    });

    chatInput.addEventListener('blur', () => {
        if (chatInput.value === '') {
            chatInput.placeholder = 'Ask questions about Kaustubh';
        }
    });

    function addDisclaimerMessage() {
        if (!disclaimerAdded) {
            const disclaimerMessage = document.createElement('div');
            disclaimerMessage.classList.add('bot-message', 'disclaimer');
            disclaimerMessage.innerHTML = "<strong>Note:</strong> This is a demonstration of a project! <br> Responses may not be 100% accurate. While answers to Kaustubh’s professional queries are \"mostly\" reliable, informal questions lead to hallucinated responses. They’ve been kept in for fun! :)"
            
            // Add disclaimer as first element in chat
            if (chatMessages.firstChild) {
                chatMessages.insertBefore(disclaimerMessage, chatMessages.firstChild);
            } else {
                chatMessages.appendChild(disclaimerMessage);
            }
            
            disclaimerAdded = true;
            chatMessages.scrollTop = 0; // Scroll to top to see disclaimer
        }
    }

    function expandChatBox() {
        if (!isExpanded) {
            chatBoxContainer.classList.add('expanded');
            chatMessages.classList.add('expanded');
            isExpanded = true;
            
            // Always show disclaimer message when expanding
            addDisclaimerMessage();
        }
    }

    sendButton.addEventListener('click', () => {
        const messageText = chatInput.value;
        if (messageText.trim() !== '') {
            expandChatBox();

            // User message
            const userMessage = document.createElement('div');
            userMessage.classList.add('user-message');
            userMessage.textContent = messageText;
            chatMessages.appendChild(userMessage);

            // Bot message
            const botMessage = document.createElement('div');
            botMessage.classList.add('bot-message');
            botMessage.textContent = '...'; // loading dots
            chatMessages.appendChild(botMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            // Call FastAPI backend
            fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: {
                "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: messageText })
            })
            .then(response => response.json())
            .then(data => {
                botMessage.textContent = data.response; // replace dots with real reply
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                botMessage.textContent = "Error: could not reach the chatbot.";
                console.error("Fetch error:", error);
            });

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
            
            // Reset the disclaimerAdded flag when closing the chat
            // This ensures the disclaimer will be added again when reopening
            disclaimerAdded = false;
        }
    });

    chatInput.addEventListener('focus', () => {
        if (!isExpanded && chatMessages.children.length > 0) {
            expandChatBox();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.keyCode === 27 && isExpanded) {
            chatBoxContainer.classList.remove('expanded');
            chatMessages.classList.remove('expanded');
            isExpanded = false;
            chatInput.blur();
            
            // Reset the disclaimerAdded flag when closing the chat
            disclaimerAdded = false;
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