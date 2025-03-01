// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const imageToggleBtn = document.getElementById('imageToggleBtn');
const audioToggleBtn = document.getElementById('audioToggleBtn');
const voiceInputBtn = document.getElementById('voiceInputBtn');
const generatedImageContainer = document.getElementById('generatedImageContainer');
const generatedImage = document.getElementById('generatedImage');

// Global variables
let isImageMode = false;
let isAudioMode = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function () {
    // Event listeners
    userInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Toggle image mode
    imageToggleBtn.addEventListener('click', function () {
        isImageMode = !isImageMode;
        imageToggleBtn.classList.toggle('active', isImageMode);
    });

    // Toggle audio mode
    audioToggleBtn.addEventListener('click', function () {
        isAudioMode = !isAudioMode;
        audioToggleBtn.classList.toggle('active', isAudioMode);
    });

    // Voice input (placeholder)
    voiceInputBtn.addEventListener('click', function () {
        alert('Voice input feature is not implemented yet.');
    });
});

// Function to send message to the server
function sendMessage() {
    const message = userInput.value.trim();
    if (message === '') return;

    // Add user message to chat
    addMessage('user', message);

    // Send the request to the server
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            isImageMode: isImageMode,
            isAudioMode: isAudioMode,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            // Add bot response to chat
            addMessage('bot', data.text);

            // Show generated image if available
            if (data.image_url) {
                generatedImage.src = data.image_url;
                toggleImageDisplay(true);
            }

            // Play audio if audio mode is enabled
            if (isAudioMode && data.audio_url) {
                playAudio(data.audio_url);
            }

            // Clear the input field
            userInput.value = '';
        })
        .catch((error) => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, there was an error processing your request.');
        });
}

// Function to add a message to the chat
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    messageDiv.innerHTML = `
        <div class="message-content">${text}</div>
        <div class="message-footer">
            ${sender === 'bot' ? `<button onclick="playAudio('${text}')">🔊 Play Audio</button>` : ''}
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Function to play audio
function playAudio(audioUrl) {
    const audio = new Audio(audioUrl);
    audio.play();
}

// Function to toggle image display
function toggleImageDisplay(show = null) {
    if (show === null) {
        generatedImageContainer.style.display =
            generatedImageContainer.style.display === 'block' ? 'none' : 'block';
    } else {
        generatedImageContainer.style.display = show ? 'block' : 'none';
    }
}