# Overlay Setup Guide

Complete guide for setting up and using the Claude Computer Use overlay app.

## Overview

The overlay app provides a real-time, transparent window that shows Claude's activity as it controls your computer. It consists of:

1. **Python WebSocket Server**: Broadcasts events from Claude
2. **Electron Overlay**: Displays activity in a transparent window

## Architecture

```
Voice Input → Python Backend → WebSocket Server
                                      ↓
                              Electron Overlay
                                      ↓
                              Visual Display
```

## Prerequisites

- **Python 3.12+** with virtual environment
- **Node.js 18+** and npm
- **Anthropic API Key**
- **OpenAI API Key** (for voice control)

## Installation

### 1. Python Backend Setup

Install Python dependencies (including websockets):

```bash
# Activate your virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt
```

This installs the `websockets>=12.0` library needed for the server.

### 2. Electron Overlay Setup

Install Node.js dependencies:

```bash
cd electron-overlay
npm install
```

This installs:
- Electron 28
- React 18
- Vite 5 (build tool)
- Other dev dependencies

## Running the Overlay

### Quick Start

**Terminal 1 - Start Python backend with WebSocket server:**
```bash
python3.12 overlay_main.py
```

You should see:
```
[Overlay] Starting WebSocket server...
[WebSocket] Starting server on ws://localhost:8765
[WebSocket] Server running on ws://localhost:8765
[Overlay] Initializing voice control...
Overlay Mode Active!
```

**Terminal 2 - Start Electron overlay:**
```bash
cd electron-overlay
npm start
```

You should see:
- Vite dev server starting on http://localhost:5173
- Electron window opening in top-right corner
- DevTools opening (for debugging)

### What to Expect

1. A transparent window appears in the top-right corner
2. Status shows "Connected" with a green indicator
3. The overlay is click-through (mouse passes through it)
4. When you speak a command, activity appears in real-time

## Usage

### Voice Commands

With both terminals running, speak commands:

```
"Claude, save an image of a cat to the desktop"
"Claude, open Safari and search for recipes"
"Claude, create a note about the meeting"
```

### What You'll See

The overlay displays:

1. **Instruction**: Your command
2. **Assistant Messages**: Claude's thoughts
3. **Tool Outputs**: Results from bash, computer, or other tools
4. **Screenshots**: When Claude takes screenshots
5. **Errors**: If any tools fail

Each message has:
- Icon indicating type
- Timestamp
- Color-coded left border
- Auto-scroll to latest

## Customization

### Window Position and Size

Edit `electron-overlay/electron/main.js`:

```javascript
// Change these values
const windowWidth = 400;     // Width in pixels
const windowHeight = 600;    // Height in pixels

// Position (top-right corner by default)
const x = screenWidth - windowWidth - 20;
const y = 20;
```

Common positions:
- **Top-right**: `x = screenWidth - windowWidth - 20; y = 20`
- **Top-left**: `x = 20; y = 20`
- **Bottom-right**: `x = screenWidth - windowWidth - 20; y = screenHeight - windowHeight - 20`

### Styling

Edit `electron-overlay/src/App.css`:

```css
/* Change background transparency */
.overlay-container {
  background: rgba(0, 0, 0, 0.6);  /* 0.0-1.0 for opacity */
  backdrop-filter: blur(20px);     /* Blur amount */
}

/* Change accent colors */
.message-instruction {
  border-left: 3px solid #3b82f6;  /* Blue */
}
```

### Enable/Disable Click-through

**To make overlay interactive** (not click-through):

Edit `electron-overlay/electron/main.js` and comment out:
```javascript
// mainWindow.setIgnoreMouseEvents(true, { forward: true });
```

Now you can click buttons in the overlay (like the Clear button).

### WebSocket Port

Default is `localhost:8765`. To change:

**Backend** - `computer_use_demo/websocket_server.py`:
```python
await start_server(host="localhost", port=YOUR_PORT)
```

**Frontend** - `electron-overlay/src/App.jsx`:
```javascript
const ws = new WebSocket('ws://localhost:YOUR_PORT');
```

## Troubleshooting

### "Client disconnected" in Python terminal

**Cause**: Electron app isn't running or can't connect to WebSocket.

**Fix**:
1. Check Electron is running: `cd electron-overlay && npm start`
2. Check WebSocket server started (should see "Server running on ws://localhost:8765")
3. Look at Electron DevTools console for errors

### Overlay window not transparent

**Cause**: macOS transparency settings or permissions.

**Fix**:
1. Go to **System Settings** > **Accessibility**
2. Turn off "Reduce transparency"
3. Grant Terminal accessibility permissions

### Overlay not showing activity

**Cause**: WebSocket not connected or Python not broadcasting.

**Fix**:
1. Check overlay shows "Connected" (green indicator)
2. Verify Python terminal shows `[WebSocket] Client connected`
3. Speak a command and check Python terminal for broadcast messages
4. Look at DevTools console in Electron for WebSocket errors

### "Cannot find module 'websockets'"

**Cause**: Python dependency not installed.

**Fix**:
```bash
source venv/bin/activate
pip install websockets
```

### Vite dev server won't start

**Cause**: Port 5173 already in use.

**Fix**:
```bash
# Find and kill process using port 5173
lsof -ti:5173 | xargs kill -9

# Or change port in vite.config.js:
server: {
  port: 5174  // Different port
}
```

### DevTools showing 404 errors

**Cause**: Vite dev server not ready when Electron starts.

**Fix**: Wait a few seconds and reload Electron (`Cmd+R` in window).

## Development Tips

### Hot Reload

Changes to React code (`.jsx`, `.css`) automatically reload in Electron thanks to Vite.

### Debugging WebSocket

**Python side:**
```python
# Add to websocket_server.py
print(f"[WebSocket] Broadcasting: {event_data}")
```

**Electron side:**
Open DevTools and check Console tab for WebSocket messages.

### Building for Production

Build the overlay app:
```bash
cd electron-overlay
npm run build
```

Then run without dev server:
```bash
npm run electron
```

## Integration with Other Scripts

### Use with CLI (no voice)

Modify `main.py` to enable WebSocket:

```python
await run_computer_use(instruction, api_key, enable_websocket=True)
```

Then start WebSocket server separately:
```python
# In a separate script or background task
import asyncio
from computer_use_demo.websocket_server import start_server

asyncio.run(start_server())
```

### Custom Event Types

Add new event types in `main.py`:

```python
if enable_websocket:
    asyncio.create_task(broadcast_event({
        "type": "custom_event",
        "data": your_data
    }))
```

Handle in `App.jsx`:

```javascript
case 'custom_event':
  // Handle your custom event
  break;
```

## Advanced Configuration

### Multiple Overlays

Run multiple Electron instances on different ports:

1. Change Vite port in `vite.config.js`
2. Update WebSocket URL in `App.jsx`
3. Run with different `NODE_ENV`

### Persistent Position

Electron can save window position. Add to `main.js`:

```javascript
// Save position on close
mainWindow.on('close', () => {
  const bounds = mainWindow.getBounds();
  // Save bounds to file or localStorage
});

// Restore on create
createWindow() {
  // Load saved bounds
  // Use in BrowserWindow options
}
```

## Performance

### Message Limits

If overlay gets slow with many messages, add message limit in `App.jsx`:

```javascript
const addMessage = (message) => {
  setMessages((prev) => {
    const updated = [...prev, { ...message, id: Date.now() + Math.random() }];
    // Keep only last 100 messages
    return updated.slice(-100);
  });
};
```

### Screenshot Size

Screenshots are sent as base64 and can be large. To reduce:

1. Compress in Python before sending
2. Send URL instead of base64
3. Display thumbnail only in overlay

## Security Notes

- Overlay runs on localhost only
- WebSocket has no authentication (local use)
- Screenshots contain sensitive information
- Click-through prevents accidental clicks

For production use, add authentication to WebSocket server.

