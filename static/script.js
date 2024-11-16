// Handle user input and get the response
function getResponse() {
    const userInput = document.getElementById('user-input').value;
    if (userInput) {
        printMessage(userInput, 'user'); // Show user input
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
                if (data.image_url) {
                    displayImageInConversation(data.image_url);
                } else {
                    printMessage(data.result, 'assistant');
                }
            } else {
                printMessage(data.result, 'assistant');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            printMessage("Something went wrong, please try again.", 'assistant');
        });
    }
}

// Start voice recognition
function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-in';

    recognition.onstart = function () {
        console.log('Voice recognition started.');
    };

    recognition.onspeechend = function () {
        recognition.stop();
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        printMessage(transcript, 'user');
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
                printMessage(data.result, 'assistant');
                if (data.image_url) {
                    displayImageInConversation(data.image_url);
                }
            } else {
                printMessage(data.result, 'assistant');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            printMessage("Something went wrong, please try again.", 'assistant');
        });
    };

    recognition.start();
}

// Get CSRF token from cookies
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, "csrftoken".length + 1) === "csrftoken=") {
                cookieValue = decodeURIComponent(cookie.substring("csrftoken".length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Display messages in the conversation
function printMessage(message, sender) {
    const conversationDiv = document.getElementById('conversation');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender);
    messageDiv.textContent = message;
    conversationDiv.appendChild(messageDiv);
    conversationDiv.scrollTo({
        top: conversationDiv.scrollHeight,
        behavior: 'smooth',
    });
}

// Display images in the conversation
function displayImageInConversation(imageUrl) {
    const conversationDiv = document.getElementById('conversation');
    const imageDiv = document.createElement('div');
    const img = document.createElement('img');
    img.src = imageUrl;
    img.alt = "Assistant's Image";
    img.style.maxWidth = '100%';
    imageDiv.appendChild(img);
    conversationDiv.appendChild(imageDiv);
    conversationDiv.scrollTo({
        top: conversationDiv.scrollHeight,
        behavior: 'smooth',
    });
}

// Download conversation as PDF
function downloadPDF() {
    const conversationDiv = document.getElementById('conversation');
    const messages = conversationDiv.querySelectorAll('div');
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    let yPosition = 10;

    // Maximum page height for pdf is around 280 units, keeping space for header and margins
    const maxHeight = 280;
    
    // Loop through each message and add it to the PDF
    messages.forEach((message) => {
        const text = message.textContent.trim();
        if (text) {
            const sender = message.classList.contains('user') ? 'User: ' : 'Assistant: ';
            const fullText = sender + text;

            // Split the text into lines to prevent overflow
            const lines = doc.splitTextToSize(fullText, 180); // Adjust line width to fit page

            // Check if adding this line will exceed the max height of the page
            if (yPosition + lines.length * 10 > maxHeight) { // Adding lines with padding
                doc.addPage();
                yPosition = 10; // Reset y position for the new page
            }

            // Add text lines to the PDF
            lines.forEach((line, index) => {
                doc.text(line, 10, yPosition + index * 10); 
            });

            yPosition += lines.length * 10 + 5; // Adding space between messages
        }
    });

    // Save the PDF
    doc.save('conversation.pdf');
}
