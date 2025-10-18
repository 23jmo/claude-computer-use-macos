"""
Overlay entry point for Claude computer use.
Starts WebSocket server and listens for voice commands with overlay support.
"""

import asyncio
import os
import sys

from computer_use_demo.websocket_server import start_server
from computer_use_demo.voice_control import VoiceListener
from computer_use_demo.tts import get_tts_manager
from main import run_computer_use


async def overlay_control_loop():
    """
    Main loop for overlay-enabled computer use.
    Runs WebSocket server and listens for voice commands.
    """
    # Get API keys from environment
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
    openai_api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_KEY_HERE")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY", "YOUR_DEEPGRAM_KEY_HERE")
    
    # Validate API keys
    if anthropic_api_key == "YOUR_API_KEY_HERE":
        raise ValueError(
            "Please set your ANTHROPIC_API_KEY environment variable"
        )
    if openai_api_key == "YOUR_OPENAI_KEY_HERE":
        raise ValueError(
            "Please set your OPENAI_API_KEY environment variable"
        )
    
    # Initialize TTS manager (using macOS built-in TTS, no API key needed)
    print("[Overlay] Initializing text-to-speech...")
    tts_manager = get_tts_manager()
    if tts_manager:
        print("[Overlay] Text-to-speech enabled (macOS built-in TTS)")
    else:
        print("[Overlay] Text-to-speech disabled")
    
    # Start WebSocket server in background
    print("[Overlay] Starting WebSocket server...")
    server_task = asyncio.create_task(start_server())
    
    # Wait a bit for server to start
    await asyncio.sleep(1)
    
    # Initialize voice listener
    print("[Overlay] Initializing voice control...")
    voice_listener = VoiceListener(api_key=openai_api_key)
    
    print("\n" + "="*60)
    print("Overlay Mode Active!")
    print("="*60)
    print("WebSocket Server: ws://localhost:8765")
    print("Voice Control: Say 'Claude' followed by your command")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Main listening loop
    try:
        while True:
            try:
                print("🎤 Listening... (speak now)")
                
                # Listen for wake word and command
                command = voice_listener.listen_once()
                
                if command:
                    print(f"\n✓ Command detected: '{command}'")
                    print("-" * 60)
                    
                    # Execute the command with WebSocket broadcasting enabled
                    try:
                        await run_computer_use(
                            command, 
                            anthropic_api_key,
                            enable_websocket=True,
                            tts_manager=tts_manager
                        )
                        print("-" * 60)
                        print("✓ Command completed!\n")
                    except Exception as e:
                        print(f"Error executing command: {e}\n")
                        print("-" * 60)
                else:
                    # No wake word detected - keep listening
                    print("(No wake word detected, continuing to listen...)")
                    
            except KeyboardInterrupt:
                print("\n\nStopping overlay mode...")
                break
            except Exception as e:
                print(f"\nError in voice control loop: {e}")
                print("Continuing to listen...\n")
    finally:
        # Cancel server task
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


def main():
    """Entry point for overlay mode."""
    try:
        asyncio.run(overlay_control_loop())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

