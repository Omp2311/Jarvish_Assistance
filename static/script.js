// Function to capture user input and send it to Django for processing
function getResponse() {
    const userInput = document.getElementById('user-input').value;
    if (userInput) {
        printMessage(userInput, 'user');
        document.getElementById('user-input').value = '';
        
        fetch('/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ query: userInput })
        })
        .then(response => response.json())
        .then(data => {
            const assistantResponse = data.result;
            printMessage(assistantResponse, 'assistant');
        })
        .catch(error => console.error('Error:', error));
    }
}

// Function to start voice recognition and send the result to Django
function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-in';

    recognition.onstart = function() {
        console.log('Voice recognition started. Try speaking into the microphone.');
    }

    recognition.onspeechend = function() {
        console.log('You were quiet for a while, so voice recognition stopped.');
        recognition.stop();
    }

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        printMessage(transcript, 'user');
        
        // Send the transcript to Django for processing
        fetch('/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),  // Include CSRF token
            },
            body: JSON.stringify({ query: transcript }) // Fixed from userInput to transcript
        })
        .then(response => response.json())
        .then(data => {
            const assistantResponse = data.result;
            printMessage(assistantResponse, 'assistant');
        })
        .catch(error => console.error('Error:', error));
        
    };

    recognition.start();
}

// Function to get CSRF token for AJAX calls
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, "csrftoken".length + 1) === ("csrftoken" + '=')) {
                cookieValue = decodeURIComponent(cookie.substring("csrftoken".length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Function to print messages to the conversation div
function printMessage(message, sender) {
    const conversationDiv = document.getElementById('conversation');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender);  // 'user' or 'assistant'
    messageDiv.textContent = message;
    conversationDiv.appendChild(messageDiv);
    conversationDiv.scrollTop = conversationDiv.scrollHeight; // Scroll to the bottom
}
