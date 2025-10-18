/**
 * Electron main process for transparent overlay window
 * Creates a frameless, transparent, always-on-top, click-through window
 */

import { app, BrowserWindow, screen } from "electron";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow = null;

// Create the transparent overlay window
function createWindow() {
  // Get primary display dimensions
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width: screenWidth, height: screenHeight } =
    primaryDisplay.workAreaSize;

  // Window dimensions
  const windowWidth = 400;
  const windowHeight = 600;

  // Position in top-right corner
  const x = screenWidth - windowWidth - 20;
  const y = 20;

  mainWindow = new BrowserWindow({
    width: windowWidth,
    height: windowHeight,
    x: x,
    y: y,
    // Make window frameless and transparent
    frame: false,
    transparent: true,
    // Always on top
    alwaysOnTop: true,
    // Remove from dock/taskbar
    skipTaskbar: false,
    // Window behavior
    resizable: true,
    movable: true,
    minimizable: false,
    maximizable: false,
    closable: true,
    // macOS specific
    titleBarStyle: "customButtonsOnHover",
    vibrancy: "under-window",
    visualEffectState: "active",
    // Web preferences
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });

  // Enable click-through (mouse events pass through)
  mainWindow.setIgnoreMouseEvents(true, { forward: true });

  // Load the app
  const isDev = process.env.NODE_ENV === "development";

  if (isDev) {
    // Development: Load from Vite dev server
    mainWindow.loadURL("http://localhost:5173");
    // Open DevTools in development
    mainWindow.webContents.openDevTools({ mode: "detach" });
  } else {
    // Production: Load from built files
    mainWindow.loadFile(path.join(__dirname, "../dist/index.html"));
  }

  // Handle window closed
  mainWindow.on("closed", () => {
    mainWindow = null;
  });

  console.log("[Electron] Overlay window created");
}

// App lifecycle
app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

// Handle errors
process.on("uncaughtException", (error) => {
  console.error("[Electron] Uncaught exception:", error);
});
