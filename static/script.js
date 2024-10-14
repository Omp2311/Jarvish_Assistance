// Function to handle the user input and get the response
function getResponse() {
    const userInput = document.getElementById('user-input').value;
    if (userInput) {
        printMessage(userInput, 'user');  // Show user input
        document.getElementById('user-input').value = '';

        // Send POST request to the server with the query
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
            if (data.success) {
                // Check if it's an image-only result
                if (data.image_url) {
                    // Display the image and no text
                    displayImages(data.image_url);
                } else {
                    // Otherwise, display the assistant's response (text result)
                    const assistantResponse = data.result;
                    printMessage(assistantResponse, 'assistant');
                }
            } else {
                printMessage(data.result, 'assistant');  // Error message
            }
        })
        .catch(error => {
            console.error('Error:', error);
            printMessage("Something went wrong, please try again.", 'assistant');
        });
    }
}

// Function to start the voice recognition
function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-in';  // Set the recognition language

    recognition.onstart = function() {
        console.log('Voice recognition started. Try speaking into the microphone.');
    };

    recognition.onspeechend = function() {
        console.log('You were quiet for a while, so voice recognition stopped.');
        recognition.stop();  // Stop recognition if there's no speech
    };

    recognition.onresult = function(event) {
        // Get the transcript of what the user said
        const transcript = event.results[0][0].transcript;
        printMessage(transcript, 'user');  // Display the user's spoken input

        // Send the transcript to the server via POST request
        fetch('/search/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ query: transcript })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const assistantResponse = data.result;

                // Display the assistant's response (text result)
                if (assistantResponse) {
                    printMessage(assistantResponse, 'assistant');
                }

                // If an image URL is returned, display the image
                if (data.image_url) {
                    displayImages(data.image_url);
                }
            } else {
                printMessage(data.result || "No response received.", 'assistant');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            printMessage("Something went wrong, please try again.", 'assistant');
        });
    };

    // Start voice recognition
    recognition.start();
}

// Function to get CSRF token from the browser's cookies
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

// Function to display messages in the conversation history
function printMessage(message, sender) {
    const conversationDiv = document.getElementById('conversation');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender);  // 'user' or 'assistant'
    messageDiv.textContent = message;
    conversationDiv.appendChild(messageDiv);

    // Smooth scroll to the bottom after adding new messages
    conversationDiv.scrollTo({
        top: conversationDiv.scrollHeight,
        behavior: 'smooth'
    });
}
function appendImages(imageUrl) {
    const imageContainer = document.getElementById('image-results');
    const image = document.createElement('img');
    image.src = imageUrl;
    imageContainer.appendChild(image); // Append the new image without replacing the old ones
}
// Function to display images returned from the assistant
function displayImages(imageUrl) {
    const imageContainer = document.getElementById('image-results');
    const image = document.createElement('img');
    image.src = imageUrl;
    imageContainer.innerHTML = '';  // Clear previous images
    imageContainer.appendChild(image);
}
