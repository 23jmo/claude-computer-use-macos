# Claude Computer Use - Overlay App

A transparent, always-on-top Electron overlay that displays real-time activity from Claude Computer Use.

## Features

- **Transparent Window**: Glassmorphism design with backdrop blur
- **Click-through**: Mouse events pass through to apps below
- **Always On Top**: Stays visible while Claude works
- **Real-time Updates**: WebSocket connection to Python backend
- **Activity Display**: Shows instructions, assistant messages, tool outputs, and screenshots

## Setup

1. Install dependencies:
```bash
npm install
```

2. Make sure the Python backend WebSocket server is running (see main README)

## Development

Run in development mode (with hot reload):
```bash
npm start
```

This will:
- Start Vite dev server on http://localhost:5173
- Launch Electron with the overlay window
- Enable DevTools for debugging

## Build for Production

Build the React app:
```bash
npm run build
```

Run the built app:
```bash
npm run electron
```

## Usage

1. Start the Python backend with overlay support:
```bash
python overlay_main.py
```

2. In a separate terminal, start the Electron overlay:
```bash
cd electron-overlay
npm start
```

3. The overlay will appear in the top-right corner of your screen

4. Speak a command starting with "Claude" - you'll see real-time updates in the overlay

## Architecture

- **Electron Main Process**: Creates transparent, frameless window (`electron/main.js`)
- **React App**: Displays activity feed with WebSocket client (`src/App.jsx`)
- **WebSocket**: Connects to `ws://localhost:8765` for real-time events
- **Vite**: Build tool and dev server

## Customization

### Window Position/Size

Edit `electron/main.js`:
```javascript
const windowWidth = 400;  // Change width
const windowHeight = 600; // Change height
const x = screenWidth - windowWidth - 20; // Change x position
const y = 20; // Change y position
```

### Styling

Edit `src/App.css` to customize colors, transparency, and layout.

### Click-through Behavior

To disable click-through (make window interactive):

In `electron/main.js`, comment out:
```javascript
// mainWindow.setIgnoreMouseEvents(true, { forward: true });
```

## Troubleshooting

**Overlay not connecting:**
- Ensure Python backend is running with `overlay_main.py`
- Check WebSocket server is on `ws://localhost:8765`
- Look for connection errors in Electron DevTools console

**Window not transparent:**
- macOS may require accessibility permissions
- Try toggling "Reduced transparency" in System Preferences

**Can't interact with overlay:**
- Click-through is enabled by default
- Disable it in `electron/main.js` if you need interactive controls

