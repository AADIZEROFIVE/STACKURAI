document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');
    const suggestionChips = document.querySelectorAll('.chip');
    
    // Get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    
    // Function to add a message to the chat
    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        
        const avatarIcon = document.createElement('i');
        avatarIcon.className = isUser ? 'fas fa-user' : 'fas fa-balance-scale';
        avatarDiv.appendChild(avatarIcon);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        // Process content to add paragraph tags
        // Split by double newlines to create paragraphs
        const paragraphs = content.split('\n\n');
        paragraphs.forEach(paragraph => {
            if (paragraph.trim()) {
                const p = document.createElement('p');
                // Process single newlines as line breaks
                p.innerHTML = paragraph.replace(/\n/g, '<br>');
                contentDiv.appendChild(p);
            }
        });
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
    
    // Add loading indicator
    function addLoadingIndicator() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.id = 'loading-message';
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        
        const avatarIcon = document.createElement('i');
        avatarIcon.className = 'fas fa-balance-scale';
        avatarDiv.appendChild(avatarIcon);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'loading-content';
        
        const loadingDotsDiv = document.createElement('div');
        loadingDotsDiv.className = 'loading-dots';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            loadingDotsDiv.appendChild(dot);
        }
        
        contentDiv.appendChild(loadingDotsDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
    
    // Remove loading indicator
    function removeLoadingIndicator() {
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }
    
    // Function to handle errors
    function handleError(errorMessage) {
        removeLoadingIndicator();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = errorMessage;
        
        chatMessages.appendChild(errorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Remove the error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    // Process user input and get response
    async function processUserInput(userMessage) {
        // Clear the input field
        userInput.value = '';
        
        // Add user message to chat
        addMessage(userMessage, true);
        
        // Add loading indicator
        addLoadingIndicator();
        
        try {
            // Updated endpoint to match Django URLs
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ user_input: userMessage })
            });
            
            // Remove loading indicator
            removeLoadingIndicator();
            
            if (!response.ok) {
                throw new Error(`Error: ${response.status} - ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                handleError(data.error);
            } else {
                // Add bot response to chat
                addMessage(data.response);
            }
        } catch (error) {
            console.error('Error:', error);
            handleError('Sorry, there was an error processing your request. Please try again later.');
        }
    }
    
    // Form submission handler
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const userMessage = userInput.value.trim();
        
        if (userMessage) {
            processUserInput(userMessage);
        }
    });
    
    // Suggestion chip handler
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            userInput.value = question;
            processUserInput(question);
        });
    });
    
    // Focus on input when page loads
    userInput.focus();
});