"""
Text-to-Speech module using macOS built-in TTS.
Handles audio generation and playback for Claude's assistant messages.
"""

import subprocess
import threading
from typing import Optional


class TTSManager:
    """
    Manages text-to-speech operations using macOS built-in 'say' command.
    Handles audio generation and playback in a non-blocking manner.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize TTS manager (api_key parameter kept for compatibility).
        
        Args:
            api_key: Not used, kept for compatibility with existing code
        """
        print("[TTS] Initializing macOS built-in TTS...")
        self.is_initialized = True
        print("[TTS] Audio system initialized successfully (using macOS 'say' command)")
    
    def speak(self, text: str) -> None:
        """
        Convert text to speech and play it in the background using macOS 'say' command.
        
        Args:
            text: Text to convert to speech
        """
        print(f"[TTS] speak() called with text: {text[:50]}...")
        if not self.is_initialized:
            print("[TTS] Audio system not initialized, skipping speech")
            return
        
        if not text or not text.strip():
            print("[TTS] Empty text, skipping speech")
            return
        
        try:
            print("[TTS] Starting macOS TTS...")
            # Use macOS built-in 'say' command in a separate thread to avoid blocking
            def speak_thread():
                try:
                    # Clean the text for better speech (remove markdown formatting)
                    clean_text = text.replace('*', '').replace('_', '').replace('`', '')
                    subprocess.run(['say', clean_text], check=True)
                    print("[TTS] macOS TTS completed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"[TTS] Error with macOS 'say' command: {e}")
                except Exception as e:
                    print(f"[TTS] Unexpected error during speech: {e}")
            
            # Start speech in background thread
            thread = threading.Thread(target=speak_thread, daemon=True)
            thread.start()
            print("[TTS] TTS thread started")
            
        except Exception as e:
            print(f"[TTS] Error starting speech: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources (no cleanup needed for macOS 'say' command)."""
        print("[TTS] Cleanup completed (no resources to clean up)")


# Global TTS manager instance (initialized when needed)
_tts_manager: Optional[TTSManager] = None


def get_tts_manager(api_key: Optional[str] = None) -> Optional[TTSManager]:
    """
    Get or create TTS manager instance.
    
    Args:
        api_key: Not used, kept for compatibility with existing code
        
    Returns:
        TTSManager instance (always succeeds with macOS built-in TTS)
    """
    global _tts_manager
    
    print(f"[TTS] get_tts_manager called (macOS built-in TTS)")
    
    if _tts_manager is None:
        try:
            print("[TTS] Creating new TTSManager instance")
            _tts_manager = TTSManager(api_key)
            print("[TTS] TTSManager created successfully")
        except Exception as e:
            print(f"[TTS] Failed to initialize TTS manager: {e}")
            return None
    else:
        print("[TTS] Returning existing TTSManager instance")
    
    return _tts_manager


def cleanup_tts() -> None:
    """Clean up global TTS manager."""
    global _tts_manager
    if _tts_manager:
        _tts_manager.cleanup()
        _tts_manager = None
