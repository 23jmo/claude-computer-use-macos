"""
Simple test script for WebSocket server.
Run this to verify the WebSocket server works before connecting the overlay.
"""

import asyncio
from computer_use_demo.websocket_server import start_server, broadcast_event


async def test_broadcast():
    """Test broadcasting messages to connected clients."""
    # Wait a moment for server to be ready
    await asyncio.sleep(2)
    
    print("\n[Test] Starting broadcast test...")
    print("[Test] Connect your overlay or a WebSocket client to ws://localhost:8765")
    print("[Test] Press Ctrl+C to stop\n")
    
    # Simulate different types of events
    test_events = [
        {
            "type": "instruction",
            "text": "Test instruction: Save an image to desktop"
        },
        {
            "type": "assistant_message",
            "text": "I'll help you save an image to the desktop."
        },
        {
            "type": "tool_output",
            "tool_id": "test_001",
            "output": "Command executed successfully"
        },
        {
            "type": "status",
            "status": "Task completed"
        }
    ]
    
    try:
        for i, event in enumerate(test_events):
            print(f"[Test] Broadcasting event {i+1}/{len(test_events)}: {event['type']}")
            await broadcast_event(event)
            await asyncio.sleep(3)  # Wait 3 seconds between events
        
        print("\n[Test] All test events sent!")
        print("[Test] Server will continue running. Press Ctrl+C to stop.")
        
        # Keep running
        await asyncio.Future()
        
    except KeyboardInterrupt:
        print("\n[Test] Stopping test...")


async def main():
    """Run WebSocket server and test broadcaster."""
    print("="*60)
    print("WebSocket Server Test")
    print("="*60)
    print("Starting WebSocket server on ws://localhost:8765")
    print("This will broadcast test events every 3 seconds")
    print("="*60 + "\n")
    
    # Start server in background
    server_task = asyncio.create_task(start_server())
    
    # Start test broadcaster
    test_task = asyncio.create_task(test_broadcast())
    
    try:
        await asyncio.gather(server_task, test_task)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        server_task.cancel()
        test_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest complete.")

