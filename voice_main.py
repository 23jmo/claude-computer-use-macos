"""
Voice-controlled entry point for Claude computer use.
Continuously listens for "claude" wake word and executes voice commands.
"""

import asyncio
import os
import sys

from computer_use_demo.voice_control import VoiceListener
from main import run_computer_use


async def voice_control_loop():
    """
    Main loop for voice-controlled computer use.
    Continuously listens for wake word and executes commands.
    """
    # Get API keys from environment
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
    openai_api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY_HERE")
    
    # Validate API keys
    if anthropic_api_key == "YOUR_API_KEY_HERE":
        raise ValueError(
            "Please set your ANTHROPIC_API_KEY environment variable"
        )
    if openai_api_key == "YOUR_OPENAI_KEY_HERE":
        raise ValueError(
            "Please set your OPENAI_API_KEY environment variable"
        )
    
    # Initialize voice listener
    print("Initializing voice control...")
    print("Setting up microphone and Whisper API...")
    voice_listener = VoiceListener(api_key=openai_api_key)
    
    print("\n" + "="*60)
    print("Voice Control Active!")
    print("="*60)
    print("Say 'Claude' followed by your command.")
    print("Example: 'Claude, save an image of a cat to the desktop'")
    print("Press Ctrl+C to stop.")
    print("="*60 + "\n")
    
    # Main listening loop
    while True:
        try:
            print("🎤 Listening... (speak now)")
            
            # Listen for wake word and command
            command = voice_listener.listen_once()
            
            if command:
                print(f"\n✓ Command detected: '{command}'")
                print("-" * 60)
                
                # Execute the command using Claude computer use
                try:
                    await run_computer_use(command, anthropic_api_key)
                    print("-" * 60)
                    print("✓ Command completed!\n")
                except Exception as e:
                    print(f"Error executing command: {e}\n")
                    print("-" * 60)
            else:
                # No wake word detected - keep listening
                print("(No wake word detected, continuing to listen...)")
                
        except KeyboardInterrupt:
            print("\n\nStopping voice control...")
            break
        except Exception as e:
            print(f"\nError in voice control loop: {e}")
            print("Continuing to listen...\n")


def main():
    """Entry point for voice-controlled mode."""
    try:
        asyncio.run(voice_control_loop())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

