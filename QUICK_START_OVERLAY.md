# Quick Start: Overlay App

Get the Claude overlay running in 5 minutes.

## Prerequisites

- Python 3.12+ virtual environment already set up
- Node.js 18+ installed ([Download](https://nodejs.org/))
- API keys configured in `.env` or environment

## Step 1: Install Python Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate

# Install/update dependencies (includes websockets)
pip install -r requirements.txt
```

## Step 2: Install Electron Dependencies

```bash
cd electron-overlay
npm install
```

This takes 2-3 minutes to download Node dependencies.

## Step 3: Start Backend

**Open Terminal 1:**

```bash
# From project root
python3.12 overlay_main.py
```

**Expected output:**
```
[Overlay] Starting WebSocket server...
[WebSocket] Starting server on ws://localhost:8765
[WebSocket] Server running on ws://localhost:8765
[Overlay] Initializing voice control...

============================================================
Overlay Mode Active!
============================================================
WebSocket Server: ws://localhost:8765
Voice Control: Say 'Claude' followed by your command
Press Ctrl+C to stop
============================================================

🎤 Listening... (speak now)
```

## Step 4: Start Overlay

**Open Terminal 2:**

```bash
cd electron-overlay
npm start
```

**Expected output:**
```
> claude-overlay@1.0.0 start
> concurrently "npm run dev" "wait-on http://localhost:5173 && npm run electron-dev"

VITE v5.0.8  ready in 543 ms
➜  Local:   http://localhost:5173/
[Electron] Overlay window created
```

**What you'll see:**
- A transparent window appears in the **top-right corner**
- Status shows **"Connected"** with green indicator
- DevTools window opens (you can close it or keep for debugging)

## Step 5: Test It

**Speak a command:**
```
"Claude, save an image of a cat to the desktop"
```

**Watch the overlay:**
- Your instruction appears
- Claude's thoughts appear
- Tool outputs show in real-time
- Screenshots display as thumbnails

## Quick Tips

### Window Too Small?

Edit `electron-overlay/electron/main.js`:
```javascript
const windowWidth = 500;   // Change from 400
const windowHeight = 800;  // Change from 600
```

Restart Electron (Ctrl+C in Terminal 2, then `npm start` again).

### Want to Click Buttons in Overlay?

Edit `electron-overlay/electron/main.js` and comment out:
```javascript
// mainWindow.setIgnoreMouseEvents(true, { forward: true });
```

### Clear Old Messages?

If click-through is disabled, click the **Clear** button in the overlay header.

### Stop Everything?

Press **Ctrl+C** in both terminals.

## Troubleshooting

### "Cannot import websockets"
```bash
source venv/bin/activate
pip install websockets
```

### Overlay Shows "Disconnected"
- Check Terminal 1 shows "Server running"
- Restart both terminals
- Check no firewall blocking localhost

### Electron Won't Start
```bash
cd electron-overlay
rm -rf node_modules
npm install
```

### Port 5173 Already in Use
```bash
lsof -ti:5173 | xargs kill -9
```

## Next Steps

- Read [OVERLAY_SETUP.md](OVERLAY_SETUP.md) for detailed configuration
- Read [OVERLAY_IMPLEMENTATION.md](OVERLAY_IMPLEMENTATION.md) for architecture details
- Customize styling in `electron-overlay/src/App.css`
- Adjust window position in `electron-overlay/electron/main.js`

## One-Line Test

Test WebSocket server without voice control:

```bash
python test_websocket.py
```

Then start overlay in another terminal. You'll see test messages broadcast every 3 seconds.

---

**That's it!** You now have a transparent overlay showing Claude's activity in real-time.

