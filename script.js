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

    sendButton.addEventListener('click', () => {
        sendButton.classList.add('translucent');
        setTimeout(() => {
            sendButton.classList.remove('translucent');
        }, 300); // Adjust the timeout as needed
    });
});
