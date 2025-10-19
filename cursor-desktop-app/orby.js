class OrbyVoiceAssistant {
  constructor() {
    console.log("Orby Voice Assistant initializing...");

    // WebSocket connection
    this.ws = null;
    this.wsUrl = "ws://localhost:8765";
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;

    // Cursor state machine
    this.currentState = "idle"; // idle, listening, thinking, moving, clicking, typing, complete
    this.stateHistory = [];

    // Initialize visual state to idle
    this.updateVisualState();

    // Interaction tracking
    this.hoverStartTime = null;
    this.hoverThreshold = 1000; // 1 second for long hover
    this.hoverTimer = null;

    // Position tracking
    this.currentPosition = { x: 0, y: 0 };
    this.targetPosition = { x: 0, y: 0 };

    this.initializeWebSocket();
    this.initializeEventListeners();
    this.initializeIPC();
    console.log("Orby Voice Assistant ready!");
  }

  initializeWebSocket() {
    this.connectWebSocket();
  }

  initializeIPC() {
    // Listen for cursor move events from main process
    if (typeof require !== "undefined") {
      const { ipcRenderer } = require("electron");
      ipcRenderer.on("cursor-move", (event, coordinates) => {
        this.moveCursorTo(coordinates);
      });

      // Store IPC renderer for window control
      this.ipcRenderer = ipcRenderer;
    }
  }

  setWindowInteractive(interactive) {
    // Enable or disable window interactivity
    if (this.ipcRenderer) {
      this.ipcRenderer.invoke("set-ignore-mouse-events", !interactive);
      this.ipcRenderer.invoke("set-focusable", interactive);
    }
  }

  connectWebSocket() {
    try {
      this.ws = new WebSocket(this.wsUrl);

      this.ws.onopen = () => {
        console.log("WebSocket connected to backend");
        this.reconnectAttempts = 0;
        // Don't set state here - wait for backend to send initial state
      };

      this.ws.onmessage = (event) => {
        console.log("WebSocket message received:", event.data);
        this.handleWebSocketMessage(event.data);
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        this.setState("idle");
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    } catch (error) {
      console.error("Failed to connect WebSocket:", error);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
      );
      setTimeout(() => {
        this.connectWebSocket();
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error("Max reconnection attempts reached");
    }
  }

  handleWebSocketMessage(data) {
    try {
      const message = JSON.parse(data);
      console.log("WebSocket message:", message);

      switch (message.type) {
        case "connection":
          console.log("Connected to backend:", message.message);
          break;

        case "state_change":
          // Backend actively sends state updates
          console.log("State change received:", message.state);

          // Handle wakeword detected state
          if (message.state === "wakeword_detected") {
            this.setState("wakeword_detected");
            // After transition completes, go to listening state
            setTimeout(() => this.setState("listening"), 1500);
          } else {
            // Handle all other states including idle state
            console.log(`Setting state to: ${message.state}`);
            this.setState(message.state);
          }
          break;

        case "instruction":
          this.setState("thinking");
          break;

        case "assistant_message":
          // Keep thinking state while processing
          console.log("Assistant message received:", message.text);
          break;

        case "tool_output":
          if (
            message.output.includes("click") ||
            message.output.includes("Click")
          ) {
            this.setState("clicking");
            // Return to idle after click animation
            setTimeout(() => this.setState("idle"), 500);
          } else if (
            message.output.includes("type") ||
            message.output.includes("Typed")
          ) {
            this.setState("typing");
            // Return to idle after typing animation
            setTimeout(() => this.setState("idle"), 1000);
          } else if (
            message.output.includes("move") ||
            message.output.includes("Move")
          ) {
            this.setState("moving");
            // Return to idle after movement
            setTimeout(() => this.setState("idle"), 300);
          } else if (
            message.output.includes("completed") ||
            message.output.includes("successfully") ||
            message.output.includes("finished")
          ) {
            this.setState("complete");
            // Return to idle after completion animation
            setTimeout(() => this.setState("idle"), 1500);
          }
          break;

        case "cursor_action":
          console.log(
            "Cursor action event received:",
            message.action,
            message.coordinates
          );
          this.handleCursorAction(message);
          break;

        case "screenshot":
          this.setState("thinking");
          break;

        case "tool_error":
          console.error("Tool error:", message.error);
          this.setState("idle");
          break;

        case "command_complete":
          // Command sequence finished
          this.setState("complete");
          setTimeout(() => this.setState("idle"), 1500);
          break;
      }
    } catch (error) {
      console.error("Error parsing WebSocket message:", error);
    }
  }

  handleCursorAction(message) {
    console.log("Handling cursor action:", message);

    if (message.action === "mouse_move" && message.coordinates) {
      this.targetPosition = message.coordinates;
      this.setState("moving");
      this.moveCursorTo(message.coordinates);
      // Return to idle after movement
      setTimeout(() => this.setState("idle"), 300);
    } else if (message.action === "click") {
      this.setState("clicking");
      setTimeout(() => this.setState("idle"), 500);
    } else if (message.action === "type") {
      this.setState("typing");
      setTimeout(() => this.setState("idle"), 1000);
    } else if (message.action === "drag") {
      this.setState("moving");
      if (message.coordinates) {
        this.moveCursorTo(message.coordinates);
      }
      setTimeout(() => this.setState("idle"), 500);
    }
  }

  moveCursorTo(coordinates) {
    const container = document.querySelector(".container");
    if (container && coordinates) {
      console.log("Moving cursor to:", coordinates);

      // Update target position
      this.targetPosition = { x: coordinates.x, y: coordinates.y };

      // Apply smooth CSS transition
      container.style.left = `${coordinates.x}px`;
      container.style.top = `${coordinates.y}px`;
      container.style.transform = "translate(-50%, -50%)";

      // Update current position after transition
      this.currentPosition = { ...this.targetPosition };
    } else {
      console.log("Could not move cursor - container or coordinates missing:", {
        container,
        coordinates,
      });
    }
  }

  setState(newState) {
    if (this.currentState !== newState) {
      console.log(`State transition: ${this.currentState} → ${newState}`);
      this.stateHistory.push({
        from: this.currentState,
        to: newState,
        timestamp: Date.now(),
      });

      this.currentState = newState;
      this.updateVisualState();
    } else {
      console.log(`State already ${newState}, skipping update`);
    }
  }

  initializeEventListeners() {
    const logo = document.getElementById("orby-logo");
    if (logo) {
      console.log("Logo found, adding interaction listeners");

      // Enable mouse events when hovering over the Orby button
      logo.addEventListener("mouseenter", () => {
        this.setWindowInteractive(true);
        this.hoverStartTime = Date.now();
        this.hoverTimer = setTimeout(() => {
          console.log("Long hover detected");
          this.handleLongHover();
        }, this.hoverThreshold);
      });

      // Disable mouse events when leaving the Orby button
      logo.addEventListener("mouseleave", () => {
        // Only disable if we're not showing the text input overlay
        if (!document.querySelector(".text-input-overlay")) {
          this.setWindowInteractive(false);
        }
        if (this.hoverTimer) {
          clearTimeout(this.hoverTimer);
          this.hoverTimer = null;
        }
        this.hoverStartTime = null;
      });

      // Quick click detection
      logo.addEventListener("click", (e) => {
        e.preventDefault();
        console.log("Quick click detected");
        this.handleQuickClick();
      });
    } else {
      console.error("Logo element not found!");
    }
  }

  handleQuickClick() {
    // Show text input for manual command entry (voice is always listening)
    console.log("Click detected - showing text input");
    this.showTextInput();
  }

  handleLongHover() {
    // Show text input for manual command entry
    this.showTextInput();
  }

  showTextInput() {
    // Make window interactive to allow text input
    this.setWindowInteractive(true);

    // Create text input overlay
    const inputOverlay = document.createElement("div");
    inputOverlay.className = "text-input-overlay";
    inputOverlay.innerHTML = `
            <input type="text" id="manual-command" placeholder="Enter command..." />
            <button id="send-command">Send</button>
            <button id="cancel-command">Cancel</button>
        `;

    document.body.appendChild(inputOverlay);

    // Focus on input after a short delay to ensure window is ready
    setTimeout(() => {
      const input = document.getElementById("manual-command");
      if (input) {
        input.focus();
      }
    }, 100);

    // Handle send
    document.getElementById("send-command").addEventListener("click", () => {
      const command = document.getElementById("manual-command").value.trim();
      if (command && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(
          JSON.stringify({
            type: "manual_command",
            command: command,
          })
        );
        this.setState("thinking");
      }
      document.body.removeChild(inputOverlay);
      // Restore click-through behavior
      this.setWindowInteractive(false);
    });

    // Handle cancel
    document.getElementById("cancel-command").addEventListener("click", () => {
      document.body.removeChild(inputOverlay);
      // Restore click-through behavior
      this.setWindowInteractive(false);
    });

    // Handle escape key
    const handleKeyPress = (e) => {
      if (e.key === "Escape") {
        document.body.removeChild(inputOverlay);
        document.removeEventListener("keydown", handleKeyPress);
        // Restore click-through behavior
        this.setWindowInteractive(false);
      } else if (e.key === "Enter") {
        document.getElementById("send-command").click();
        document.removeEventListener("keydown", handleKeyPress);
      }
    };
    document.addEventListener("keydown", handleKeyPress);
  }

  updateVisualState() {
    const logo = document.getElementById("orby-logo");
    const listeningText = document.getElementById("listening-text");
    const cursorGraphic = document.querySelector(".cursor-graphic");

    // Remove all state classes
    logo.classList.remove(
      "listening",
      "thinking",
      "moving",
      "clicking",
      "typing",
      "complete",
      "wakeword_detected"
    );

    // Add current state class
    if (this.currentState !== "idle") {
      logo.classList.add(this.currentState);
    }

    // Add listening class to cursor-graphic for the second shape
    if (cursorGraphic) {
      if (this.currentState === "listening") {
        cursorGraphic.classList.add("listening");
      } else {
        cursorGraphic.classList.remove("listening");
      }
    }

    // Show/hide listening text based on state
    if (listeningText) {
      if (this.currentState === "listening") {
        listeningText.classList.add("show");
      } else {
        listeningText.classList.remove("show");
      }
    }

    console.log(`Visual state updated to: ${this.currentState}`);
  }
}

// Initialize Orby when the page loads
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, initializing Orby...");
  new OrbyVoiceAssistant();
});

// Also try initializing after a short delay in case DOM isn't ready
setTimeout(() => {
  if (!window.orbyInstance) {
    console.log("Fallback initialization...");
    window.orbyInstance = new OrbyVoiceAssistant();
  }
}, 1000);
