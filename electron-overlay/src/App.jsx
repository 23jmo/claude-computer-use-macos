/**
 * Main React component for Claude overlay
 * Connects to WebSocket server and displays real-time computer use activity
 */

import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  // State for WebSocket connection
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [currentInstruction, setCurrentInstruction] = useState('');
  const [currentState, setCurrentState] = useState('idle'); // idle, listening, processing
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Connect to WebSocket server
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8765');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WebSocket] Connected to backend');
        setConnected(true);
        // Set initial state to listening since the backend starts listening immediately
        setCurrentState('listening');
      };

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected from backend');
        setConnected(false);
        setCurrentState('idle');
        
        // Attempt to reconnect after 3 seconds
        setTimeout(() => {
          console.log('[WebSocket] Attempting to reconnect...');
          connectWebSocket();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WebSocket] Received:', data);
          
          // Handle different event types
          switch (data.type) {
            case 'connection':
              // Connection confirmation
              break;
            
            case 'state_change':
              console.log('[WebSocket] State change:', data.state);
              setCurrentState(data.state);
              break;
            
            case 'instruction':
              setCurrentInstruction(data.text);
              addMessage({
                type: 'instruction',
                text: data.text,
                timestamp: new Date()
              });
              break;
            
            case 'assistant_message':
              addMessage({
                type: 'assistant',
                text: data.text,
                timestamp: new Date()
              });
              break;
            
            case 'tool_output':
              addMessage({
                type: 'tool',
                toolId: data.tool_id,
                text: data.output,
                timestamp: new Date()
              });
              break;
            
            case 'tool_error':
              addMessage({
                type: 'error',
                toolId: data.tool_id,
                text: data.error,
                timestamp: new Date()
              });
              break;
            
            case 'screenshot':
              addMessage({
                type: 'screenshot',
                toolId: data.tool_id,
                base64: data.base64,
                timestamp: new Date()
              });
              break;
            
            default:
              console.log('[WebSocket] Unknown event type:', data.type);
          }
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Add a message to the list
  const addMessage = (message) => {
    setMessages((prev) => [...prev, { ...message, id: Date.now() + Math.random() }]);
  };

  // Clear all messages
  const clearMessages = () => {
    setMessages([]);
    setCurrentInstruction('');
    setCurrentState('idle');
  };

  return (
    <div className="overlay-container">
      {/* Header */}
      <div className="overlay-header">
        <div className="header-content">
          <span className="title">Claude Activity</span>
          <div className="status">
            <span className={`status-indicator ${connected ? 'connected' : 'disconnected'}`} />
            <span className="status-text">{connected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
        {messages.length > 0 && (
          <button className="clear-button" onClick={clearMessages}>
            Clear
          </button>
        )}
      </div>

      {/* Current Instruction */}
      {currentInstruction && (
        <div className="current-instruction">
          <div className="instruction-label">Current Task:</div>
          <div className="instruction-text">{currentInstruction}</div>
        </div>
      )}

      {/* Messages */}
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className={`state-display state-${currentState}`}>
            {currentState === 'idle' && (
              <div className="idle-state">
                <div className="idle-icon">🤖</div>
                <div className="idle-text">Ready</div>
              </div>
            )}
            {currentState === 'listening' && (
              <div className="listening-state">
                <div className="listening-text">Listening</div>
                <div className="listening-shapes">
                  <div className="listening-shape shape-1"></div>
                  <div className="listening-shape shape-2"></div>
                </div>
              </div>
            )}
            {currentState === 'processing' && (
              <div className="processing-state">
                <div className="processing-icon">⚡</div>
                <div className="processing-text">Processing...</div>
              </div>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message message-${message.type}`}>
              {message.type === 'instruction' && (
                <>
                  <div className="message-header">📋 New Instruction</div>
                  <div className="message-body">{message.text}</div>
                </>
              )}
              
              {message.type === 'assistant' && (
                <>
                  <div className="message-header">💭 Claude</div>
                  <div className="message-body">{message.text}</div>
                </>
              )}
              
              {message.type === 'tool' && (
                <>
                  <div className="message-header">🔧 Tool Output</div>
                  <div className="message-body tool-output">{message.text}</div>
                </>
              )}
              
              {message.type === 'error' && (
                <>
                  <div className="message-header">⚠️ Error</div>
                  <div className="message-body error-text">{message.text}</div>
                </>
              )}
              
              {message.type === 'screenshot' && (
                <>
                  <div className="message-header">📸 Screenshot</div>
                  <div className="message-body">
                    <img 
                      src={`data:image/png;base64,${message.base64}`} 
                      alt="Screenshot"
                      className="screenshot-thumbnail"
                    />
                  </div>
                </>
              )}
              
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default App;

