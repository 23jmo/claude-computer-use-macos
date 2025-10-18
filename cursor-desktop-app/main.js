const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  // Create the browser window as a true floating widget
  const mainWindow = new BrowserWindow({
    width: 250,
    height: 100,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      backgroundThrottling: false,
      webSecurity: false,
      allowRunningInsecureContent: true
    },
    frame: false, // Remove window frame
    transparent: true, // Make window transparent
    resizable: false,
    alwaysOnTop: true, // Keep on top
    skipTaskbar: true, // Don't show in taskbar
    titleBarStyle: 'hidden',
    hasShadow: false, // Remove shadow
    backgroundColor: 'rgba(0,0,0,0)', // Fully transparent
    type: 'desktop', // Make it behave like a desktop widget
    focusable: false, // Don't steal focus
    show: false, // Don't show until ready
    vibrancy: 'under-window', // macOS vibrancy effect
    visualEffectState: 'active',
    opacity: 1.0 // Full opacity for the window
  });

  // Load the index.html file
  mainWindow.loadFile('index.html');

  // Position the window in the top-right corner
  const { screen } = require('electron');
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;
  
  mainWindow.setPosition(width - 270, 20); // Top-right corner with some margin

  // Show the window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Make sure it stays on top
  mainWindow.setAlwaysOnTop(true, 'screen-saver');

  // Make the window draggable
  mainWindow.setMovable(true);

  // Ensure complete transparency
  mainWindow.setBackgroundColor('rgba(0,0,0,0)');

  // Open DevTools for debugging (disabled for clean UI)
  // mainWindow.webContents.openDevTools();
}

// This method will be called when Electron has finished initialization
app.whenReady().then(createWindow);

// Quit when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
