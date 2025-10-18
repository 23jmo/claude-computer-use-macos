import asyncio
import os
import sys
import json
import base64
import dotenv
from computer_use_demo.loop import sampling_loop, APIProvider
from computer_use_demo.tools import ToolResult
from anthropic.types.beta import BetaMessage, BetaMessageParam
from anthropic import APIResponse
from computer_use_demo.websocket_server import broadcast_event
from computer_use_demo.tts import get_tts_manager

dotenv.load_dotenv()


async def run_computer_use(instruction: str, api_key: str, provider: APIProvider = APIProvider.ANTHROPIC, enable_websocket: bool = False, tts_manager=None):
    """
    Run Claude computer use with the given instruction.
    This is the core function that can be called from voice control or CLI.
    
    Args:
        instruction: The command/instruction for Claude to execute
        api_key: Anthropic API key
        provider: API provider (default: ANTHROPIC)
        enable_websocket: If True, broadcast events to WebSocket clients
        tts_manager: Optional TTS manager for text-to-speech output
    
    Returns:
        List of messages from the conversation
    """
    print(
        f"Starting Claude 'Computer Use'.\nPress ctrl+c to stop.\nInstructions provided: '{instruction}'"
    )
    print(f"[DEBUG] TTS manager status: {'AVAILABLE' if tts_manager else 'NOT AVAILABLE'}")

    # Broadcast initial instruction to WebSocket clients
    if enable_websocket:
        await broadcast_event({
            "type": "instruction",
            "text": instruction
        })

    # Set up the initial messages
    messages: list[BetaMessageParam] = [
        {
            "role": "user",
            "content": instruction,
        }
    ]

    # Define callbacks (you can customize these)
    def output_callback(content_block):
        print(f"[DEBUG] output_callback called with: {type(content_block)}")
        
        # Handle BetaTextBlock objects (Anthropic's text blocks)
        if hasattr(content_block, 'type') and content_block.type == "text":
            text_content = content_block.text
            print("Assistant:", text_content)
            
            # Broadcast assistant message to WebSocket clients
            if enable_websocket:
                asyncio.create_task(broadcast_event({
                    "type": "assistant_message",
                    "text": text_content
                }))
            
            # Speak the assistant message if TTS manager is available
            if tts_manager and text_content:
                print(f"[TTS] Speaking: {text_content[:50]}...")
                # Call synchronous speak method directly
                tts_manager.speak(text_content)
                print("[TTS] TTS call completed")
            elif not tts_manager:
                print("[TTS] No TTS manager available")
            elif not text_content:
                print("[TTS] No text content to speak")
        
        # Fallback for dictionary format (if needed)
        elif isinstance(content_block, dict) and content_block.get("type") == "text":
            text_content = content_block.get("text")
            print("Assistant:", text_content)
            
            # Broadcast assistant message to WebSocket clients
            if enable_websocket:
                asyncio.create_task(broadcast_event({
                    "type": "assistant_message",
                    "text": text_content
                }))
            
            # Speak the assistant message if TTS manager is available
            if tts_manager and text_content:
                print(f"[TTS] Speaking: {text_content[:50]}...")
                # Call synchronous speak method directly
                tts_manager.speak(text_content)
                print("[TTS] TTS call completed")
            elif not tts_manager:
                print("[TTS] No TTS manager available")
            elif not text_content:
                print("[TTS] No text content to speak")

    def tool_output_callback(result: ToolResult, tool_use_id: str):
        if result.output:
            print(f"> Tool Output [{tool_use_id}]:", result.output)
            
            # Broadcast tool output to WebSocket clients
            if enable_websocket:
                asyncio.create_task(broadcast_event({
                    "type": "tool_output",
                    "tool_id": tool_use_id,
                    "output": result.output
                }))
        
        if result.error:
            print(f"!!! Tool Error [{tool_use_id}]:", result.error)
            
            # Broadcast tool error to WebSocket clients
            if enable_websocket:
                asyncio.create_task(broadcast_event({
                    "type": "tool_error",
                    "tool_id": tool_use_id,
                    "error": result.error
                }))
        
        if result.base64_image:
            # Save the image to a file if needed
            os.makedirs("screenshots", exist_ok=True)
            image_data = result.base64_image
            with open(f"screenshots/screenshot_{tool_use_id}.png", "wb") as f:
                f.write(base64.b64decode(image_data))
            print(f"Took screenshot screenshot_{tool_use_id}.png")
            
            # Broadcast screenshot to WebSocket clients
            if enable_websocket:
                asyncio.create_task(broadcast_event({
                    "type": "screenshot",
                    "tool_id": tool_use_id,
                    "base64": result.base64_image
                }))

    def api_response_callback(response: APIResponse[BetaMessage]):
        print(
            "\n---------------\nAPI Response:\n",
            json.dumps(json.loads(response.text)["content"], indent=4),  # type: ignore
            "\n",
        )

    # Run the sampling loop
    messages = await sampling_loop(
        model="claude-3-5-sonnet-20241022",
        provider=provider,
        system_prompt_suffix="",
        messages=messages,
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
        api_response_callback=api_response_callback,
        api_key=api_key,
        only_n_most_recent_images=10,
        max_tokens=4096,
    )
    
    return messages


async def main():
    """
    Main entry point for CLI usage.
    Maintains backward compatibility with original script.
    """
    # Set up your Anthropic API key and model
    api_key = os.getenv("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
    if api_key == "YOUR_API_KEY_HERE":
        raise ValueError(
            "Please first set your API key in the ANTHROPIC_API_KEY environment variable"
        )
    
    # Check if the instruction is provided via command line arguments
    if len(sys.argv) > 1:
        instruction = " ".join(sys.argv[1:])
    else:
        instruction = "Save an image of a cat to the desktop."
    
    # Run computer use with the instruction
    await run_computer_use(instruction, api_key)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Encountered Error:\n{e}")
