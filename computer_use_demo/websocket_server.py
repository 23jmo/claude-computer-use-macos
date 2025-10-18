"""
WebSocket server for broadcasting computer use events to overlay clients.
Provides real-time updates for assistant messages, tool outputs, and screenshots.
"""

import asyncio
import json
import websockets
from typing import Set
from websockets.server import WebSocketServerProtocol


# Store all connected clients
connected_clients: Set[WebSocketServerProtocol] = set()


async def register_client(websocket: WebSocketServerProtocol):
    """Register a new client connection."""
    connected_clients.add(websocket)
    print(f"[WebSocket] Client connected. Total clients: {len(connected_clients)}")
    
    # Send initial connection confirmation
    await websocket.send(json.dumps({
        "type": "connection",
        "status": "connected",
        "message": "Connected to computer use backend"
    }))


async def unregister_client(websocket: WebSocketServerProtocol):
    """Unregister a client connection."""
    connected_clients.discard(websocket)
    print(f"[WebSocket] Client disconnected. Total clients: {len(connected_clients)}")


async def broadcast_event(event_data: dict):
    """
    Broadcast an event to all connected clients.
    
    Args:
        event_data: Dictionary containing event information
    """
    if not connected_clients:
        return
    
    message = json.dumps(event_data)
    
    # Send to all connected clients
    disconnected = set()
    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected.add(client)
    
    # Remove disconnected clients
    for client in disconnected:
        await unregister_client(client)


async def handler(websocket: WebSocketServerProtocol):
    """Handle WebSocket client connections."""
    await register_client(websocket)
    
    try:
        # Keep connection alive and handle incoming messages
        async for message in websocket:
            # Echo back or handle client messages if needed
            pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await unregister_client(websocket)


async def start_server(host: str = "localhost", port: int = 8765):
    """
    Start the WebSocket server.
    
    Args:
        host: Host to bind to
        port: Port to listen on
    """
    print(f"[WebSocket] Starting server on ws://{host}:{port}")
    
    async with websockets.serve(handler, host, port):
        print(f"[WebSocket] Server running on ws://{host}:{port}")
        await asyncio.Future()  # Run forever


# Global reference to the broadcast function for easy import
__all__ = ['start_server', 'broadcast_event', 'connected_clients']

