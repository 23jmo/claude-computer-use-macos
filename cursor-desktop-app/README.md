# Cursor Widget

A beautiful, floating desktop widget featuring the exact glowing teal cursor design from your reference image.

## Features

- **Pure Widget Design**: Just the glowing teal cursor graphic - no background, no text
- **Floating Overlay**: Transparent, frameless widget that floats over other applications
- **Draggable**: Click and drag to move the widget anywhere on your screen
- **Glowing Animation**: Beautiful pulsing glow effect on the cursor graphic
- **Always On Top**: Stays visible while other apps are running
- **Interactive**: Hover effects and smooth transitions
- **macOS Optimized**: Native desktop widget behavior

## How to Run

1. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Start the app**:
   ```bash
   npm start
   ```

3. **Development mode**:
   ```bash
   npm run dev
   ```

## Design Details

- **Background**: Completely transparent - no background at all
- **Cursor Graphic**: Teal gradient (#00d4aa to #00b894) with intense glowing effect
- **Inner Circle**: Bright white circle with subtle glow
- **Animation**: Beautiful pulsing glow effect that intensifies and fades
- **Widget**: 200x200px, transparent, frameless, always on top, panel type

## Customization

You can easily modify:
- Colors in `styles.css`
- Text content in `index.html`
- Window properties in `main.js`
- Animation timing and effects

## File Structure

```
cursor-desktop-app/
├── main.js          # Electron main process
├── index.html       # App HTML structure
├── styles.css       # Styling and animations
├── package.json     # Dependencies and scripts
└── README.md        # This file
```

The app is now ready to use and matches your exact design requirements!
