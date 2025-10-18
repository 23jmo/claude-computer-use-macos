"""
Voice control module for Claude computer use.
Listens for wake word "orby" and transcribes voice commands using OpenAI Whisper.
"""

import os
import tempfile
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
from openai import OpenAI
from typing import Optional


class VoiceListener:
    """
    Continuously listens to microphone and transcribes audio using OpenAI Whisper API.
    Detects "orby" wake word and extracts commands.
    """
    
    def __init__(self, api_key: str, sample_rate: int = 16000, chunk_duration: int = 5):
        """
        Initialize the voice listener with continuous audio stream.

        Args:
            api_key: OpenAI API key for Whisper
            sample_rate: Audio sample rate in Hz (16kHz is optimal for Whisper)
            chunk_duration: Duration of each recording chunk in seconds
        """
        self.client = OpenAI(api_key=api_key)
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.wake_word = "orby"

        # Initialize continuous audio input stream (keeps mic open)
        print("[Voice] Opening continuous audio stream...")
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16
        )
        self.stream.start()
        print("[Voice] Microphone ready (continuous mode - no flickering)")
        
    def record_audio_chunk(self) -> np.ndarray:
        """
        Record a chunk of audio from the continuous stream.
        Microphone stays open between calls (no flickering).

        Returns:
            Audio data as numpy array
        """
        # Read from continuous stream (mic stays open)
        frames = int(self.chunk_duration * self.sample_rate)
        audio_data, overflowed = self.stream.read(frames)

        if overflowed:
            print("[Voice] Warning: Audio buffer overflow (some samples lost)")

        return audio_data
    
    def save_audio_to_temp_file(self, audio_data: np.ndarray) -> str:
        """
        Save audio data to a temporary WAV file.
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Path to the temporary WAV file
        """
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Write audio data to WAV file
        wavfile.write(temp_path, self.sample_rate, audio_data)
        return temp_path
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio file using OpenAI Whisper API.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                # Call Whisper API for transcription
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Optimize for English
                )
            return transcript.text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def extract_command(self, transcription: str) -> Optional[str]:
        """
        Extract command from transcription if wake word is detected.
        
        Args:
            transcription: Full transcription text
            
        Returns:
            Command text after wake word, or None if wake word not found
        """
        # Convert to lowercase for case-insensitive matching
        lower_text = transcription.lower()
        
        # Check if wake word is present
        if self.wake_word not in lower_text:
            return None
        
        # Find position of wake word and extract everything after it
        wake_word_index = lower_text.find(self.wake_word)
        command_start = wake_word_index + len(self.wake_word)
        
        # Extract command (from original transcription to preserve capitalization)
        command = transcription[command_start:].strip()
        
        # Remove common filler words at the start
        filler_words = ["please", "can you", "could you", "would you"]
        command_lower = command.lower()
        for filler in filler_words:
            if command_lower.startswith(filler):
                command = command[len(filler):].strip()
                command_lower = command.lower()
        
        return command if command else None
    
    def listen_once(self) -> Optional[str]:
        """
        Listen for one audio chunk and check for wake word.
        
        Returns:
            Command text if wake word detected, None otherwise
        """
        # Record audio chunk
        audio_data = self.record_audio_chunk()
        
        # Save to temporary file
        temp_path = self.save_audio_to_temp_file(audio_data)
        
        try:
            # Transcribe audio
            transcription = self.transcribe_audio(temp_path)
            
            if transcription:
                # Check for wake word and extract command
                command = self.extract_command(transcription)
                return command
            
            return None
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception:
                pass  # Ignore cleanup errors
    
    def cleanup(self):
        """Stop and close the audio stream."""
        try:
            if hasattr(self, 'stream') and self.stream.active:
                print("[Voice] Stopping audio stream...")
                self.stream.stop()
                self.stream.close()
                print("[Voice] Audio stream closed")
        except Exception as e:
            print(f"[Voice] Error closing audio stream: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.cleanup()

    def get_available_devices(self):
        """Print available audio input devices for debugging."""
        print("Available audio devices:")
        print(sd.query_devices())

