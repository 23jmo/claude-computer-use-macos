const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");

function createWindow() {
  // Get screen dimensions for full-screen overlay
  const { screen } = require("electron");
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.size;

  // Create a full-screen transparent overlay window
  const mainWindow = new BrowserWindow({
    width: width,
    height: height,
    x: 0,
    y: 0,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      backgroundThrottling: false,
      webSecurity: false,
      allowRunningInsecureContent: true,
    },
    frame: false, // Remove window frame
    transparent: true, // Make window transparent
    resizable: false,
    alwaysOnTop: true, // Keep on top
    skipTaskbar: true, // Don't show in taskbar
    titleBarStyle: "hidden",
    hasShadow: false, // Remove shadow
    backgroundColor: "rgba(0,0,0,0)", // Fully transparent
    focusable: false, // Don't steal focus
    show: false, // Don't show until ready
    opacity: 1.0, // Full opacity for the window
  });

  // Load the index.html file
  mainWindow.loadFile("index.html");

  // Store reference to mainWindow for IPC communication
  global.mainWindow = mainWindow;

  // Set up IPC handlers for cursor positioning
  ipcMain.handle("move-cursor", (event, coordinates) => {
    if (mainWindow && coordinates) {
      mainWindow.webContents.send("cursor-move", coordinates);
    }
  });

  // Show the window when ready
  mainWindow.once("ready-to-show", () => {
    mainWindow.show();
  });

  // Make sure it stays on top
  mainWindow.setAlwaysOnTop(true, "screen-saver");

  // Ensure complete transparency
  mainWindow.setBackgroundColor("rgba(0,0,0,0)");

  // Open DevTools for debugging (disabled for clean UI)
  // mainWindow.webContents.openDevTools();
}

// This method will be called when Electron has finished initialization
app.whenReady().then(createWindow);

// Quit when all windows are closed
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
