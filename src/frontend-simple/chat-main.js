// chat-main.js
// const axios = require('axios');

// # const BASE_API_URL = 'http://35.185.56.27:9000';
const BASE_API_URL = '/api';
// const BASE_API_URL = 'http://localhost:9000';
console.log("BASE_API_URL:", BASE_API_URL)

function uuid() {
    const newUuid = ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
        (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16),
    )
    return newUuid;
}


// Create an axios instance with base configuration
const api = axios.create({
    baseURL: BASE_API_URL
});
const sessionId = uuid();
// Add request interceptor to include session ID in headers
api.interceptors.request.use((config) => {
    if (sessionId) {
        config.headers['X-Session-ID'] = sessionId;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// DOM Elements
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');
const header = document.querySelector('.header');

// Hamburger Menu Toggle
if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        hamburger.classList.toggle('active');
    });
}

// Sticky Header
let lastScroll = 0;
window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > lastScroll) {
        header.classList.add('scroll-down');
        header.classList.remove('scroll-up');
    } else {
        header.classList.add('scroll-up');
        header.classList.remove('scroll-down');
    }

    lastScroll = currentScroll <= 0 ? 0 : currentScroll;
});


const DataService = {
    GetChat: async function (model, chat_id) {
        const response = await api.get(`/${model}/chats/${chat_id}`);
        return response.data;
    },
    StartChatWithLLM: async function (model, message) {
        const response = await api.post(`/${model}/chats/`, message);
        return response.data;
    },
    ContinueChatWithLLM: async function (model, chat_id, message) {
        const response = await api.post(`/${model}/chats/${chat_id}`, message);
        return response.data;
    },
};

class ChatApp {
    constructor() {
        this.chatHistory = document.getElementById('chatHistory');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.fileInput = document.getElementById('fileInput');
        this.previewImg = document.getElementById('previewImg');
        this.model = "llm-rag";

        this.currentChatId = null;
        this.isTyping = false;

        this.setupEventListeners();
        this.adjustTextAreaHeight();
        
;
    }

    setupEventListeners() {
        this.messageInput.addEventListener('input', () => {
            this.adjustTextAreaHeight();
            this.updateSendButton();
        });

        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        this.sendButton.addEventListener('click', () => this.handleSendMessage());
    }

    adjustTextAreaHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = `${this.messageInput.scrollHeight}px`;
    }

    updateSendButton() {
        this.sendButton.disabled = !this.messageInput.value.trim();
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.innerHTML = `
            <div class="message-icon">
                <i class="fas fa-martini-glass-citrus" style="color: #e55c2a;"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        typingDiv.id = 'typingIndicator';
        this.chatHistory.appendChild(typingDiv);
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
        this.isTyping = true;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
        this.isTyping = false;
    }

    async handleSendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
    
        const messageData = {
            content: message,
            timestamp: new Date().toISOString()
        };
        
        this.appendMessage('user', messageData);

        // Clear input
        this.messageInput.value = '';
        this.adjustTextAreaHeight();
        this.updateSendButton();
    
        // Show typing indicator
        this.showTypingIndicator();
    
        try {
            let response;
            if (this.currentChatId) {
                // Continue existing chat
                response = await DataService.ContinueChatWithLLM(
                    this.model,
                    this.currentChatId,
                    messageData
                );
            } else {
                // Start new chat
                response = await DataService.StartChatWithLLM(
                    this.model,
                    messageData
                );
                this.currentChatId = response.chat_id;
            }
    
            // Hide typing indicator
            this.hideTypingIndicator();
    
            // Add assistant response to chat
            this.appendMessage('assistant', {
                content: response.messages[response.messages.length - 1].content,
                timestamp: new Date(response.dts * 1000).toISOString()
            });
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.appendMessage('assistant', {
                content: 'Sorry, there was an error processing your message.',
                timestamp: new Date().toISOString()
            });
        }
    }


    formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    appendMessage(role, messageData) {
        console.log("Appending Message:", { role, messageData });
    
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
    
        // Only add the icon for assistant messages
        if (role === 'assistant') {
            const iconDiv = document.createElement('div');
            iconDiv.className = 'message-icon';
            const icon = document.createElement('i');
            icon.className = 'fas fa-martini-glass-citrus';
            icon.style.color = '#e55c2a';
            iconDiv.appendChild(icon);
            messageDiv.appendChild(iconDiv);
        }
    
        // Content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
    
        if (messageData.content) {
            const textContent = document.createElement('div');
            textContent.className = 'text-content';
            contentDiv.appendChild(textContent);
    
            // Progressive Text Rendering for Assistant Messages
            if (role === 'assistant') {
                this.typeText(textContent, messageData.content, 5, () => {
                    // Callback after text is fully rendered
                    this.addSaveButton(messageDiv, messageData);
                });
            } else {
                textContent.innerHTML = marked.parse(messageData.content);
            }
        }
    
        if (messageData.timestamp) {
            const timeSpan = document.createElement('span');
            timeSpan.className = 'message-time';
            timeSpan.textContent = this.formatTime(messageData.timestamp);
            messageDiv.appendChild(timeSpan);
        }
    
        messageDiv.appendChild(contentDiv);
    
        this.chatHistory.appendChild(messageDiv);
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
    }

    saveResponse(response) {
    const savedResponses = JSON.parse(localStorage.getItem('savedResponses')) || [];
    const alreadySaved = savedResponses.some(
        (r) => r.content === response.content && r.timestamp === response.timestamp
    );

    if (!alreadySaved) {
        savedResponses.push(response);
        localStorage.setItem('savedResponses', JSON.stringify(savedResponses));
    }
}

    viewSavedResponses() {
        const savedResponses = JSON.parse(localStorage.getItem('savedResponses')) || [];
        console.log('Saved Responses:', savedResponses);
        alert(JSON.stringify(savedResponses, null, 2)); 
    }

    addSaveButton(messageDiv, messageData) {
        const saveButton = document.createElement('button');
        saveButton.className = 'save-button';
        saveButton.title = 'Save this response';
        saveButton.innerHTML = '<i class="far fa-heart"></i>';
        saveButton.addEventListener('click', () => {
            const icon = saveButton.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.saveResponse(messageData);
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
            }
        });
    
        // Adjust position and container spacing
        saveButton.style.position = 'absolute';
        saveButton.style.top = '10px';
        saveButton.style.right = '10px';
        saveButton.style.background = 'transparent';
        saveButton.style.border = 'none';
        saveButton.style.color = '#e55c2a';
        saveButton.style.fontSize = '18px';
        saveButton.style.cursor = 'pointer';
    
        // Add padding to prevent overlap
        messageDiv.style.position = 'relative';
        messageDiv.style.paddingRight = '40px'; 
        messageDiv.appendChild(saveButton);
    }
    
    // Smooth typing 
    typeText(element, text, speed = 50, callback = null) {
        
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = marked.parse(text);
    
        const formattedText = tempContainer.innerHTML; 
        element.innerHTML = ''; 
    
        let i = 0;
        const interval = setInterval(() => {
            if (i < formattedText.length) {
                element.innerHTML = formattedText.slice(0, i + 1); 
                i++;
            } else {
                clearInterval(interval); 
                if (callback) callback(); 
            }
        }, speed);
    }
}

// Initialize the chat app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
});