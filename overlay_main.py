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
from computer_use_demo.voice_control import VoiceListener
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
            # Broadcast listening state
            await broadcast_event({"type": "state_change", "state": "listening"})
            print("🎤 Listening for 'Orby' wake word...")
            
            # Listen for wake word and command
            command = voice_listener.listen_once()
            
            if command:
                print(f"\n✓ Command detected: '{command}'")
                print("-" * 60)
                
                # Broadcast processing state
                await broadcast_event({"type": "state_change", "state": "processing"})
                
                # Execute the command with WebSocket broadcasting enabled
                try:
                    await run_computer_use(
                        command, 
                        anthropic_api_key,
                        enable_websocket=True,
                        tts_manager=tts_manager
                    )
                    print("-" * 60)
                    print("✓ Command completed! Returning to listening...\n")
                except Exception as e:
                    print(f"Error executing command: {e}\n")
                    print("-" * 60)
                    # Return to listening even after errors
                    await broadcast_event({"type": "state_change", "state": "idle"})
            # Loop continues automatically - always listening
            
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
    
    # Enhanced WebSocket server will be started later
    
    # Initialize voice listener
    print("[Overlay] Initializing voice control...")
    voice_listener = VoiceListener(api_key=openai_api_key)
    
    print("\n" + "="*60)
    print("Overlay Mode Active!")
    print("="*60)
    print("WebSocket Server: ws://localhost:8765")
    print("Voice Control: Always listening for 'Orby' wake word")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    # Store the voice listener and other components for WebSocket handler
    global_anthropic_api_key = anthropic_api_key
    global_tts_manager = tts_manager
    
    # Enhanced WebSocket handler that can process manual text commands
    async def enhanced_websocket_handler(websocket):
        """Enhanced WebSocket handler that processes manual text commands from frontend."""
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type")
                    
                    if msg_type == "manual_command":
                        command = data.get("command")
                        if command:
                            print(f"\n✓ Manual command received: '{command}'")
                            print("-" * 60)
                            
                            # Execute the command with WebSocket broadcasting enabled
                            try:
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
                
                except json.JSONDecodeError:
                    print(f"[WebSocket] Invalid JSON received: {message}")
                except Exception as e:
                    print(f"[WebSocket] Error processing message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print("[WebSocket] Client disconnected")
        except Exception as e:
            print(f"[WebSocket] Error in handler: {e}")
    
    # Start the enhanced WebSocket server and continuous voice loop
    print("[Overlay] Starting enhanced WebSocket server...")
    async with websockets.serve(enhanced_websocket_handler, "localhost", 8765):
        print("[Overlay] Enhanced WebSocket server running on ws://localhost:8765")
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
        
        # Keep the server running
        try:
            await voice_task  # Wait for voice loop (runs forever)
        except KeyboardInterrupt:
            print("\n\nStopping overlay mode...")
            voice_task.cancel()
            try:
                await voice_task
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

