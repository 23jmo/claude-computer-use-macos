class OrbyVoiceAssistant {
    constructor() {
        console.log('Orby Voice Assistant initializing...');
        this.isListening = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.backendUrl = 'http://localhost:8000/api/voice'; // Orby API server endpoint
        
        this.initializeEventListeners();
        this.requestMicrophonePermission();
        console.log('Orby Voice Assistant ready!');
    }

    initializeEventListeners() {
        const logo = document.getElementById('orby-logo');
        if (logo) {
            console.log('Logo found, adding click listener');
            logo.addEventListener('click', () => {
                console.log('Orby button clicked!');
                this.toggleListening();
            });
        } else {
            console.error('Logo element not found!');
        }
    }

    async requestMicrophonePermission() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            stream.getTracks().forEach(track => track.stop()); // Stop the stream, we just needed permission
            console.log('Microphone permission granted');
        } catch (error) {
            console.error('Microphone permission denied:', error);
        }
    }

    async toggleListening() {
        console.log('Toggle listening called, current state:', this.isListening);
        if (this.isListening) {
            this.stopListening();
        } else {
            await this.startListening();
        }
    }

    async startListening() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };

            this.mediaRecorder.onstop = () => {
                this.processAudio();
            };

            this.mediaRecorder.start();
            this.isListening = true;
            this.updateVisualState();
            
            console.log('Orby is now listening...');
            
            // Auto-stop after 10 seconds
            setTimeout(() => {
                if (this.isListening) {
                    this.stopListening();
                }
            }, 10000);

        } catch (error) {
            console.error('Error starting voice recording:', error);
        }
    }

    stopListening() {
        if (this.mediaRecorder && this.isListening) {
            this.mediaRecorder.stop();
            this.isListening = false;
            this.updateVisualState();
            console.log('Orby stopped listening');
        }
    }

    async processAudio() {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'voice-input.wav');

            const response = await fetch(this.backendUrl, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Backend response:', result);
                this.handleBackendResponse(result);
            } else {
                console.error('Backend error:', response.statusText);
            }
        } catch (error) {
            console.error('Error sending audio to backend:', error);
        }
    }

    handleBackendResponse(response) {
        // Handle the response from your backend
        // This could include:
        // - Displaying text responses
        // - Executing system commands
        // - Playing audio responses
        // - Updating UI elements
        
        console.log('Processing backend response:', response);
        
        // Example: If backend returns a text response
        if (response.text) {
            this.showNotification(response.text);
        }
        
        // Example: If backend returns a command to execute
        if (response.command) {
            this.executeCommand(response.command);
        }
    }

    showNotification(message) {
        // Create a temporary notification
        const notification = document.createElement('div');
        notification.className = 'orby-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 3000);
    }

    executeCommand(command) {
        // Execute system commands or other actions
        console.log('Executing command:', command);
        // You can integrate with your existing computer use tools here
    }

    updateVisualState() {
        const logo = document.getElementById('orby-logo');
        const listeningText = document.getElementById('listening-text');
        
        if (this.isListening) {
            logo.classList.add('listening');
            listeningText.classList.add('show');
        } else {
            logo.classList.remove('listening');
            listeningText.classList.remove('show');
        }
    }
}

// Initialize Orby when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Orby...');
    new OrbyVoiceAssistant();
});

// Also try initializing after a short delay in case DOM isn't ready
setTimeout(() => {
    if (!window.orbyInstance) {
        console.log('Fallback initialization...');
        window.orbyInstance = new OrbyVoiceAssistant();
    }
}, 1000);
