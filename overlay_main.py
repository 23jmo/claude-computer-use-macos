"""
Overlay entry point for Claude computer use.
Starts WebSocket server and listens for voice commands with overlay support.
"""

import asyncio
import os
import sys
import json
import websockets

from computer_use_demo.websocket_server import start_server, broadcast_event
from computer_use_demo.voice_control_deepgram import VoiceListenerDeepgram
from computer_use_demo.tts import get_tts_manager
from main import run_computer_use


async def continuous_voice_loop(voice_listener, anthropic_api_key, tts_manager):
    """
    Continuous listening loop that automatically listens for "orby" wake word.
    Runs forever, executing commands and returning to listening state.
    
    Args:
        voice_listener: VoiceListener instance
        anthropic_api_key: Anthropic API key
        tts_manager: TTS manager for speech output
    """
    print("[Continuous Loop] Starting continuous voice listening...")
    
    while True:
        try:
            # Start in idle state - waiting for wake word
            await broadcast_event({"type": "state_change", "state": "idle"})
            print("🎤 Waiting for 'Orby' wake word...")
            
            # Listen for wake word and command
            command = voice_listener.listen_once()
            
            if command:
                print(f"\n✓ Command detected: '{command}'")
                print("-" * 60)
                
                # Broadcast wakeword detected state for transition animation
                await broadcast_event({"type": "state_change", "state": "wakeword_detected"})
                
                # Brief delay for transition animation
                await asyncio.sleep(1.5)
                
                # Now go to listening state to record the command
                await broadcast_event({"type": "state_change", "state": "listening"})
                print("🎤 Listening for command...")
                
                # Execute the command with WebSocket broadcasting enabled
                try:
                    await run_computer_use(
                        command, 
                        anthropic_api_key,
                        enable_websocket=True,
                        tts_manager=tts_manager
                    )
                    print("-" * 60)
                    print("✓ Command completed! Returning to idle...\n")
                    
                    # Send command complete event to frontend
                    await broadcast_event({
                        "type": "command_complete",
                        "status": "success"
                    })
                except Exception as e:
                    print(f"Error executing command: {e}\n")
                    print("-" * 60)
                    # Return to idle after errors
                    await broadcast_event({"type": "state_change", "state": "idle"})
            else:
                # No wake word detected, stay in idle state
                print("No wake word detected, staying in idle state...")
                await broadcast_event({"type": "state_change", "state": "idle"})
            
        except KeyboardInterrupt:
            print("\n[Continuous Loop] Stopping...")
            break
        except Exception as e:
            print(f"[Continuous Loop] Error: {e}")
            print("Continuing to listen...")
            await broadcast_event({"type": "state_change", "state": "idle"})


async def overlay_control_loop():
    """
    Main loop for overlay-enabled computer use.
    Runs WebSocket server and listens for voice commands.
    """
    # Get API keys from environment
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
    deepgram_api_key = os.getenv("DEEPGRAM_API_KEY", "YOUR_DEEPGRAM_KEY_HERE")
    
    # Validate API keys
    if anthropic_api_key == "YOUR_API_KEY_HERE":
        raise ValueError(
            "Please set your ANTHROPIC_API_KEY environment variable"
        )
    if deepgram_api_key == "YOUR_DEEPGRAM_KEY_HERE":
        raise ValueError(
            "Please set your DEEPGRAM_API_KEY environment variable"
        )
    
    # Initialize TTS manager (using macOS built-in TTS, no API key needed)
    print("[Overlay] Initializing text-to-speech...")
    tts_manager = get_tts_manager()
    if tts_manager:
        print("[Overlay] Text-to-speech enabled (macOS built-in TTS)")
    else:
        print("[Overlay] Text-to-speech disabled")
    
    # Enhanced WebSocket server will be started later
    
    # Initialize voice listener with Deepgram
    print("[Overlay] Initializing voice control with Deepgram...")
    voice_listener = VoiceListenerDeepgram(api_key=deepgram_api_key)
    
    print("\n" + "="*60)
    print("Overlay Mode Active!")
    print("="*60)
    print("WebSocket Server: ws://localhost:8765")
    print("Voice Control: Always listening for 'Orby' wake word")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Store the voice listener and other components globally for manual commands
    global_anthropic_api_key = anthropic_api_key
    global_tts_manager = tts_manager
    
    # Function to handle manual commands from frontend
    async def handle_manual_command(command: str):
        """Handle manual command from frontend."""
        try:
            print(f"\n✓ Manual command received: '{command}'")
            print("-" * 60)
            
            # Execute the command with WebSocket broadcasting enabled
            await run_computer_use(
                command, 
                global_anthropic_api_key,
                enable_websocket=True,
                tts_manager=global_tts_manager
            )
            print("-" * 60)
            print("✓ Command completed!\n")
        except Exception as e:
            print(f"Error executing command: {e}\n")
            print("-" * 60)
    
    # Set up the message handler for manual commands
    from computer_use_demo.websocket_server import set_message_handler
    set_message_handler(handle_manual_command)
    
    # Start the WebSocket server and continuous voice loop
    print("[Overlay] Starting WebSocket server...")
    
    # Start the WebSocket server
    server_task = asyncio.create_task(start_server("localhost", 8765))
    
    # Wait a moment for server to start
    await asyncio.sleep(1)
    
    print("[Overlay] WebSocket server running on ws://localhost:8765")
    print("\n" + "="*60)
    print("Overlay Mode Active!")
    print("="*60)
    print("WebSocket Server: ws://localhost:8765")
    print("Voice Control: Continuous listening for 'Orby' commands")
    print("Frontend: Click Orby logo for text input")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Start continuous voice listening loop as background task
    voice_task = asyncio.create_task(
        continuous_voice_loop(voice_listener, anthropic_api_key, tts_manager)
    )
    
    # Keep both tasks running
    try:
        await asyncio.gather(server_task, voice_task)
    except KeyboardInterrupt:
        print("\n\nStopping overlay mode...")
        server_task.cancel()
        voice_task.cancel()
        try:
            await asyncio.gather(server_task, voice_task, return_exceptions=True)
        except Exception:
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

