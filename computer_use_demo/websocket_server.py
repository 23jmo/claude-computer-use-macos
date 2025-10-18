"""
WebSocket server for broadcasting computer use events to overlay clients.
Provides real-time updates for assistant messages, tool outputs, and screenshots.
Enhanced with heartbeat/ping-pong, reconnection support, and event queueing.
"""

import asyncio
import json
import time
import websockets
from typing import Set, Dict, List
from websockets.server import WebSocketServerProtocol
from collections import deque


# Store all connected clients with metadata
connected_clients: Dict[str, dict] = {}

# Event history for reconnecting clients (limited to last 50 events)
event_history: deque = deque(maxlen=50)

# Heartbeat interval in seconds
HEARTBEAT_INTERVAL = 30
HEARTBEAT_TIMEOUT = 60


def generate_client_id(websocket: WebSocketServerProtocol) -> str:
    """Generate a unique client ID based on remote address."""
    remote = websocket.remote_address
    return f"{remote[0]}:{remote[1]}" if remote else str(id(websocket))


async def register_client(websocket: WebSocketServerProtocol, client_id: str = None):
    """
    Register a new client connection.

    Args:
        websocket: The WebSocket connection
        client_id: Optional client ID for reconnection
    """
    if not client_id:
        client_id = generate_client_id(websocket)

    connected_clients[client_id] = {
        "websocket": websocket,
        "connected_at": time.time(),
        "last_heartbeat": time.time()
    }

    print(f"[WebSocket] Client connected: {client_id}. Total clients: {len(connected_clients)}")

    # Send initial connection confirmation with client ID
    await websocket.send(json.dumps({
        "type": "connection",
        "status": "connected",
        "client_id": client_id,
        "message": "Connected to computer use backend"
    }))

    # Send recent event history to new client
    if event_history:
        await websocket.send(json.dumps({
            "type": "event_history",
            "events": list(event_history)
        }))


async def unregister_client(client_id: str):
    """
    Unregister a client connection.

    Args:
        client_id: The client ID to unregister
    """
    if client_id in connected_clients:
        del connected_clients[client_id]
        print(f"[WebSocket] Client disconnected: {client_id}. Total clients: {len(connected_clients)}")


async def broadcast_event(event_data: dict):
    """
    Broadcast an event to all connected clients and store in history.

    Args:
        event_data: Dictionary containing event information
    """
    # Add timestamp to event
    event_data["timestamp"] = time.time()

    # Store in event history
    event_history.append(event_data)

    if not connected_clients:
        return

    message = json.dumps(event_data)

    # Send to all connected clients
    disconnected = []
    for client_id, client_data in list(connected_clients.items()):
        websocket = client_data["websocket"]
        try:
            await websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected.append(client_id)
        except Exception as e:
            print(f"[WebSocket] Error sending to client {client_id}: {e}")
            disconnected.append(client_id)

    # Remove disconnected clients
    for client_id in disconnected:
        await unregister_client(client_id)


async def heartbeat_monitor(websocket: WebSocketServerProtocol, client_id: str):
    """
    Monitor heartbeat for a client connection.

    Args:
        websocket: The WebSocket connection
        client_id: The client ID
    """
    try:
        while client_id in connected_clients:
            await asyncio.sleep(HEARTBEAT_INTERVAL)

            if client_id not in connected_clients:
                break

            client_data = connected_clients[client_id]
            time_since_heartbeat = time.time() - client_data["last_heartbeat"]

            # Check if client is still alive
            if time_since_heartbeat > HEARTBEAT_TIMEOUT:
                print(f"[WebSocket] Client {client_id} timed out")
                await unregister_client(client_id)
                break

            # Send ping
            try:
                pong = await websocket.ping()
                await asyncio.wait_for(pong, timeout=10)
                client_data["last_heartbeat"] = time.time()
            except asyncio.TimeoutError:
                print(f"[WebSocket] Ping timeout for client {client_id}")
                await unregister_client(client_id)
                break
            except Exception as e:
                print(f"[WebSocket] Heartbeat error for client {client_id}: {e}")
                await unregister_client(client_id)
                break

    except asyncio.CancelledError:
        pass


async def handler(websocket: WebSocketServerProtocol):
    """
    Handle WebSocket client connections with heartbeat monitoring.
    Supports client reconnection and message handling.
    """
    client_id = generate_client_id(websocket)
    heartbeat_task = None

    try:
        # Register client
        await register_client(websocket, client_id)

        # Start heartbeat monitor
        heartbeat_task = asyncio.create_task(heartbeat_monitor(websocket, client_id))

        # Handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type")

                # Handle different message types
                if msg_type == "ping":
                    # Respond to client ping
                    await websocket.send(json.dumps({"type": "pong"}))
                    if client_id in connected_clients:
                        connected_clients[client_id]["last_heartbeat"] = time.time()

                elif msg_type == "reconnect":
                    # Handle reconnection request
                    old_client_id = data.get("client_id")
                    print(f"[WebSocket] Reconnection request from {old_client_id} -> {client_id}")
                    # Send event history
                    if event_history:
                        await websocket.send(json.dumps({
                            "type": "event_history",
                            "events": list(event_history)
                        }))

            except json.JSONDecodeError:
                print(f"[WebSocket] Invalid JSON from client {client_id}")
            except Exception as e:
                print(f"[WebSocket] Error handling message from {client_id}: {e}")

    except websockets.exceptions.ConnectionClosed:
        print(f"[WebSocket] Connection closed for client {client_id}")
    except Exception as e:
        print(f"[WebSocket] Error in handler for client {client_id}: {e}")
    finally:
        # Cancel heartbeat task
        if heartbeat_task:
            heartbeat_task.cancel()
            try:
                await heartbeat_task
            except asyncio.CancelledError:
                pass

        # Unregister client
        await unregister_client(client_id)


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

