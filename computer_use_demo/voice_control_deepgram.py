"""
Voice control module for Claude computer use using Deepgram.
Listens for wake word "orby" and transcribes voice commands using Deepgram API.
"""

import os
import tempfile
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
from deepgram import DeepgramClient, PrerecordedOptions, FileSource
from typing import Optional


class VoiceListenerDeepgram:
    """
    Continuously listens to microphone and transcribes audio using Deepgram API.
    Detects "orby" wake word and extracts commands.
    """
    
    def __init__(self, api_key: str, sample_rate: int = 16000, chunk_duration: int = 5):
        """
        Initialize the voice listener with continuous audio stream.

        Args:
            api_key: Deepgram API key for speech-to-text
            sample_rate: Audio sample rate in Hz (16kHz is optimal for Deepgram)
            chunk_duration: Duration of each recording chunk in seconds
        """
        self.client = DeepgramClient(api_key)
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        # Comprehensive wake word variations (~40 variations)
        self.wake_words = [
            # Direct variations
            "orby", "orbi", "orbie", "orbee", "orbe",
            # Shortened forms
            "orb", "ob", "ory",
            # Initial variations (RB sound)
            "rb", "r b", "arby", "arbi", "arbee", "ar b", "r bee",
            # Common misrecognitions
            "orvy", "orvey", "horby", "horbi", "orpy", "erby", "erbi",
            # Different endings
            "orba", "orbey", "orbay", "orboy",
            # Similar sounding
            "hobby", "bobby", "derby", "herby", "curby",
            # Phonetic spellings
            "aw-bee", "or-bee", "awr-bee", "oar-bee", "ar-bee",
            "awbee", "orbee", "awrbee", "oarbee", "arbee"
        ]
        self.primary_wake_word = "orby"

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
        Transcribe audio file using Deepgram API.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                # Configure Deepgram options
                options = PrerecordedOptions(
                    model="nova-2",
                    language="en",
                    smart_format=True,
                    punctuate=True,
                    diarize=False
                )
                
                # Call Deepgram API for transcription
                response = self.client.listen.prerecorded.v("1").transcribe_file(
                    {"buffer": audio_file, "mimetype": "audio/wav"},
                    options
                )
                
                # Extract transcript text
                transcript = response.results.channels[0].alternatives[0].transcript
                return transcript.strip()
                
        except Exception as e:
            print(f"Deepgram transcription error: {e}")
            return ""
    
    def extract_command(self, transcription: str) -> Optional[str]:
        """
        Extract command from transcription if any wake word variation is detected.
        
        Args:
            transcription: Full transcription text
            
        Returns:
            Extracted command if wake word found, None otherwise
        """
        if not transcription:
            return None
            
        # Convert to lowercase for case-insensitive matching
        text = transcription.lower().strip()
        
        # Check for any wake word variation
        detected_wake_word = None
        for wake_word in self.wake_words:
            if wake_word in text:
                detected_wake_word = wake_word
                break
        
        if detected_wake_word:
            # Extract everything after the detected wake word
            parts = text.split(detected_wake_word, 1)
            if len(parts) > 1:
                command = parts[1].strip()
                if command:
                    print(f"[Voice] Wake word '{detected_wake_word}' detected")
                    print(f"[Voice] Command extracted: '{command}'")
                    return command
        
        return None
    
    def listen_once(self) -> Optional[str]:
        """
        Listen for one command and return it if detected.
        
        Returns:
            Command string if wake word and command detected, None otherwise
        """
        try:
            # Record audio chunk
            print("[Voice] Recording audio...")
            audio_data = self.record_audio_chunk()
            
            # Save to temporary file
            temp_file = self.save_audio_to_temp_file(audio_data)
            
            try:
                # Transcribe using Deepgram
                print("[Voice] Transcribing with Deepgram...")
                transcription = self.transcribe_audio(temp_file)
                
                if transcription:
                    print(f"[Voice] Transcription: '{transcription}'")
                    
                    # Extract command if wake word is present
                    command = self.extract_command(transcription)
                    return command
                else:
                    print("[Voice] No transcription received")
                    return None
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
                    
        except Exception as e:
            print(f"[Voice] Error in listen_once: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
            print("[Voice] Audio stream closed")
