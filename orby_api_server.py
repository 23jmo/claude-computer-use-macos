"""
Orby Voice Assistant API Server
Handles voice commands from the Orby desktop widget and connects to the existing voice control system.
"""

import asyncio
import json
import os
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
from openai import OpenAI
from main import run_computer_use


class OrbyAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Orby voice commands."""
    
    def __init__(self, *args, voice_listener=None, **kwargs):
        self.voice_listener = voice_listener
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests for voice processing."""
        if self.path == '/api/voice':
            self.handle_voice_request()
        else:
            self.send_error(404, "Not Found")
    
    def handle_voice_request(self):
        """Process voice audio and execute commands."""
        try:
            # Get content length
            content_length = int(self.headers['Content-Length'])
            
            # Read the audio data
            audio_data = self.rfile.read(content_length)
            
            # Save audio to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = temp_file.name
            temp_file.write(audio_data)
            temp_file.close()
            
            # Transcribe the audio
            transcription = self.voice_listener.transcribe_audio(temp_path)
            
            if transcription:
                print(f"[Orby] Transcribed: '{transcription}'")
                
                # Extract command (look for "orby" wake word)
                command = self.extract_orby_command(transcription)
                
                if command:
                    print(f"[Orby] Command detected: '{command}'")
                    
                    # Execute the command in a separate thread
                    thread = threading.Thread(
                        target=self.execute_command_async,
                        args=(command,)
                    )
                    thread.start()
                    
                    # Send success response
                    response = {
                        "status": "success",
                        "transcription": transcription,
                        "command": command,
                        "message": f"Executing: {command}"
                    }
                else:
                    # No command detected
                    response = {
                        "status": "no_command",
                        "transcription": transcription,
                        "message": "No command detected. Say 'Orby' followed by your command."
                    }
            else:
                response = {
                    "status": "error",
                    "message": "Could not transcribe audio"
                }
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"[Orby] Error processing voice request: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def extract_orby_command(self, transcription: str) -> str:
        """Extract command from transcription if 'orby' wake word is detected."""
        lower_text = transcription.lower()
        
        # Check if "orby" wake word is present
        if "orby" not in lower_text:
            return None
        
        # Find position of wake word and extract everything after it
        wake_word_index = lower_text.find("orby")
        command_start = wake_word_index + len("orby")
        
        # Extract command
        command = transcription[command_start:].strip()
        
        # Remove common filler words
        filler_words = ["please", "can you", "could you", "would you"]
        command_lower = command.lower()
        for filler in filler_words:
            if command_lower.startswith(filler):
                command = command[len(filler):].strip()
                command_lower = command.lower()
        
        return command if command else None
    
    def execute_command_async(self, command: str):
        """Execute command using the existing computer use system."""
        try:
            # Get API key from environment
            anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_api_key:
                print("[Orby] Error: ANTHROPIC_API_KEY not set")
                return
            
            # Run the command
            print(f"[Orby] Executing command: {command}")
            asyncio.run(run_computer_use(command, anthropic_api_key))
            print(f"[Orby] Command completed: {command}")
            
        except Exception as e:
            print(f"[Orby] Error executing command: {e}")
    
    def log_message(self, format, *args):
        """Override to reduce log noise."""
        pass


def create_handler(voice_listener):
    """Create a handler class with the voice listener."""
    class Handler(OrbyAPIHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, voice_listener=voice_listener, **kwargs)
    return Handler


def start_orby_server(port=8000):
    """Start the Orby API server."""
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Please set your OPENAI_API_KEY environment variable")
    
    # Initialize voice listener
    print("[Orby] Initializing voice listener...")
    voice_listener = VoiceListener(api_key=openai_api_key)
    
    # Create server
    handler = create_handler(voice_listener)
    server = HTTPServer(('localhost', port), handler)
    
    print(f"[Orby] Starting API server on http://localhost:{port}")
    print(f"[Orby] Voice endpoint: http://localhost:{port}/api/voice")
    print("[Orby] Ready to receive voice commands from Orby widget!")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Orby] Shutting down server...")
        server.shutdown()


if __name__ == "__main__":
    # Import the VoiceListener class
    from computer_use_demo.voice_control import VoiceListener
    
    start_orby_server()
