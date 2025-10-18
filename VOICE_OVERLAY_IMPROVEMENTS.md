# Voice Overlay Improvements

This document describes the enhancements made to the voice overlay system for Claude Computer Use.

## 🎯 Overview

The voice overlay system has been significantly enhanced with the following improvements:

1. **Voice Activity Detection (VAD)** - Automatic speech detection
2. **Audio Feedback** - Beep sounds for better user experience
3. **Configurable Settings** - Centralized YAML configuration
4. **Graceful Shutdown** - Proper cleanup and error handling
5. **Command Cancellation** - Stop commands mid-execution
6. **WebSocket Improvements** - Heartbeat, reconnection, event history
7. **Enhanced TTS** - Voice selection, queue management, cancellation
8. **Error Broadcasting** - Real-time error notifications to overlay

---

## ✨ New Features

### 1. Voice Activity Detection (VAD)

**File:** `computer_use_demo/voice_control.py`

The system now automatically detects when you start and stop speaking:

- **Smart Recording**: Starts recording when speech is detected
- **Auto-Stop**: Automatically stops after 1.5 seconds of silence
- **Visual Feedback**: Dots appear in terminal while speaking
- **Configurable Threshold**: Adjust sensitivity via `config.yaml`

**Benefits:**
- No more fixed 5-second recordings
- More natural interaction
- Better battery life (records only when needed)

**Configuration:**
```yaml
voice_recognition:
  vad_threshold: 0.02          # Lower = more sensitive
  vad_min_silence: 1.5         # Seconds of silence to stop
  max_recording_duration: 15   # Maximum recording length
```

---

### 2. Audio Feedback

**File:** `computer_use_demo/voice_control.py`

Audio beeps provide feedback for different events:

- **Start Recording**: Low beep (600 Hz) when recording begins
- **End Recording**: High beep (800 Hz) when recording completes
- **Error**: Long low beep (400 Hz) on transcription failure

**Benefits:**
- Know exactly when the system is listening
- No need to watch the terminal
- Clear error indication

**Configuration:**
```yaml
voice_recognition:
  enable_audio_feedback: true  # Set to false to disable beeps
```

---

### 3. Retry Logic with Exponential Backoff

**File:** `computer_use_demo/voice_control.py`

API calls now automatically retry on failure:

- **3 Retry Attempts** (configurable)
- **Exponential Backoff**: Waits 1s, 2s, 4s between retries
- **Error Reporting**: Clear messages for each retry attempt

**Benefits:**
- More reliable in poor network conditions
- Automatic recovery from temporary failures
- Clear error messages

**Configuration:**
```yaml
voice_recognition:
  max_retries: 3  # Number of retry attempts
```

---

### 4. Graceful Shutdown & Error Broadcasting

**File:** `overlay_main.py`

The system now handles shutdown and errors properly:

- **Signal Handlers**: Responds to SIGINT, SIGTERM
- **Task Cancellation**: Cancels running tasks on shutdown
- **Status Broadcasting**: Sends shutdown events to overlay
- **Clean Cleanup**: Properly closes all connections

**Status Events Broadcast:**
- `initializing` - System starting up
- `ready` - Ready for commands
- `listening` - Listening for wake word
- `processing` - Processing command
- `completed` - Command completed
- `error` - Error occurred
- `cancelled` - Command cancelled
- `shutting_down` - System shutting down
- `shutdown` - Shutdown complete

**Benefits:**
- No hanging processes
- Overlay stays in sync with backend
- Clean exit on Ctrl+C

---

### 5. Command Cancellation

**File:** `overlay_main.py`

You can now cancel commands mid-execution:

**Stop Commands:**
- "Claude, stop"
- "Claude, cancel"
- "Claude, halt"
- "Claude, abort"

**Features:**
- Cancels current running task
- Clears TTS queue
- Returns to listening mode
- Broadcasts cancellation to overlay

**Configuration:**
```yaml
commands:
  stop_words:
    - "stop"
    - "cancel"
    - "halt"
    - "abort"
```

---

### 6. WebSocket Improvements

**File:** `computer_use_demo/websocket_server.py`

Major enhancements to WebSocket reliability:

#### Heartbeat/Ping-Pong
- **Automatic Health Checks**: Pings clients every 30 seconds
- **Dead Connection Detection**: Removes unresponsive clients
- **Timeout Configuration**: Customizable timeouts

#### Reconnection Support
- **Client IDs**: Unique ID for each client
- **Event History**: Last 50 events stored
- **Automatic Replay**: Reconnecting clients get missed events

#### Event Queueing
- **History Buffer**: Maintains recent event history
- **Timestamps**: All events timestamped
- **Graceful Degradation**: Works even when clients disconnect

**Configuration:**
```yaml
websocket:
  host: "localhost"
  port: 8765
  heartbeat_interval: 30    # Seconds between pings
  heartbeat_timeout: 60     # Client timeout
  max_event_history: 50     # Events to store
```

**New WebSocket Messages:**

**From Server:**
```json
{
  "type": "connection",
  "status": "connected",
  "client_id": "127.0.0.1:54321",
  "message": "Connected to computer use backend"
}

{
  "type": "event_history",
  "events": [/* last 50 events */]
}

{
  "type": "system_status",
  "status": "listening",
  "message": "Listening for wake word...",
  "timestamp": 1234567890.123
}
```

**From Client:**
```json
{
  "type": "ping"
}

{
  "type": "reconnect",
  "client_id": "previous_client_id"
}
```

---

### 7. Enhanced Text-to-Speech

**File:** `computer_use_demo/tts.py`

Major TTS improvements:

#### Voice Selection
- **Multiple Voices**: Choose from any macOS voice
- **Voice Discovery**: `get_available_voices()` method
- **Popular Choices**: Samantha, Alex, Victoria, Karen, Moira

#### Queue Management
- **Speech Queue**: Prevents overlapping speech
- **FIFO Processing**: Speeches play in order
- **Queue Status**: Check if speaking with `is_speaking()`

#### Cancellation Support
- **Interrupt Current**: `speak(text, interrupt=True)`
- **Cancel All**: `cancel_current()` stops all speech
- **Clean Shutdown**: Proper cleanup on exit

#### Rate Control
- **Configurable Speed**: Set words per minute
- **Natural Speech**: Default 200 wpm

**Configuration:**
```yaml
text_to_speech:
  enabled: true
  voice: "Samantha"       # macOS voice name
  rate: 200               # Words per minute
  enable_queue: true      # Enable queueing
```

**Usage:**
```python
from computer_use_demo.tts import get_tts_manager

tts = get_tts_manager()

# List available voices
voices = tts.get_available_voices()
print(voices)  # ['Samantha', 'Alex', 'Victoria', ...]

# Speak with queueing
tts.speak("Hello, I'm Claude")
tts.speak("How can I help?")  # Waits for first to finish

# Interrupt current speech
tts.speak("This is urgent!", interrupt=True)

# Check if speaking
if tts.is_speaking():
    print("Still talking...")

# Cancel all speech
tts.cancel_current()
```

---

### 8. Centralized Configuration

**Files:** `config.yaml`, `computer_use_demo/config.py`

All settings are now in one place:

#### Configuration Sections:

**Voice Recognition:**
- Wake word
- VAD settings
- Audio feedback
- Retry logic

**Text-to-Speech:**
- Voice selection
- Speech rate
- Queue settings

**WebSocket:**
- Host and port
- Heartbeat settings
- Event history size

**System:**
- Debug mode
- Logging
- Claude model
- Token limits

**Commands:**
- Stop words

#### Using Configuration:

```python
from computer_use_demo.config import get_config

config = get_config()

# Get values
wake_word = config.get("voice_recognition.wake_word")
tts_voice = config.get("text_to_speech.voice")

# Set values
config.set("voice_recognition.vad_threshold", 0.03)

# Save changes
config.save()

# Reload from file
from computer_use_demo.config import reload_config
reload_config()
```

---

## 📁 File Changes Summary

### Modified Files:

1. **`computer_use_demo/voice_control.py`**
   - Added VAD with `record_with_vad()`
   - Added audio feedback with `play_beep()`
   - Added retry logic to `transcribe_audio()`
   - Added configurable parameters
   - Added `cancel()` and `reset_cancel()` methods

2. **`overlay_main.py`**
   - Added `handle_shutdown()` for graceful shutdown
   - Added signal handlers
   - Added status broadcasting
   - Added command cancellation
   - Added stop word detection
   - Improved error handling

3. **`computer_use_demo/websocket_server.py`**
   - Added heartbeat monitoring
   - Added client ID system
   - Added event history
   - Added reconnection support
   - Added message handling

4. **`computer_use_demo/tts.py`**
   - Added voice selection
   - Added queue management
   - Added cancellation support
   - Added rate control
   - Added `get_available_voices()`

5. **`requirements.txt`**
   - Added `pyyaml>=6.0`

### New Files:

1. **`config.yaml`**
   - Central configuration file
   - All customizable settings
   - Well-documented defaults

2. **`computer_use_demo/config.py`**
   - Configuration loader
   - YAML parser
   - Default values
   - Global config instance

3. **`VOICE_OVERLAY_IMPROVEMENTS.md`** (this file)
   - Documentation
   - Usage examples
   - Configuration guide

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings (Optional)

Edit `config.yaml` to customize behavior:

```yaml
voice_recognition:
  wake_word: "hey claude"  # Change wake word
  vad_threshold: 0.03      # Adjust sensitivity

text_to_speech:
  voice: "Alex"            # Change voice
  rate: 180                # Slower speech
```

### 3. Run the System

```bash
# Start backend
python overlay_main.py

# In another terminal, start overlay
cd electron-overlay
npm start
```

---

## 🎛️ Advanced Configuration

### Adjusting VAD Sensitivity

If the system is too sensitive (picks up background noise):
```yaml
voice_recognition:
  vad_threshold: 0.04  # Higher = less sensitive
```

If the system misses your voice:
```yaml
voice_recognition:
  vad_threshold: 0.015  # Lower = more sensitive
```

### Changing TTS Voice

List available voices:
```bash
say -v ?
```

Choose your favorite:
```yaml
text_to_speech:
  voice: "Victoria"  # British English
  # or: "Alex", "Samantha", "Karen", "Moira", etc.
```

### Enabling Debug Mode

```yaml
system:
  debug_mode: true
  log_file: "overlay_debug.log"
```

---

## 🐛 Troubleshooting

### Voice Control Not Working

1. Check microphone permissions
2. Verify OpenAI API key is set
3. Increase `vad_threshold` if too sensitive
4. Check `max_retries` for API failures

### TTS Not Speaking

1. Test your voice: `say "Hello"`
2. Check voice name in config
3. Verify `text_to_speech.enabled: true`
4. Check console for TTS errors

### WebSocket Connection Lost

- The system now auto-recovers
- Clients receive event history on reconnect
- Check `heartbeat_timeout` if issues persist

### System Not Shutting Down

- Press Ctrl+C
- Wait for cleanup messages
- Force kill only as last resort: `killall python`

---

## 📊 Performance Improvements

- **Faster Wake Word Detection**: VAD reduces unnecessary API calls
- **Better Resource Usage**: Recording only when speaking
- **Improved Reliability**: Retry logic and error handling
- **Smoother TTS**: Queue prevents overlapping speech
- **More Responsive**: Real-time status updates

---

## 🔮 Future Enhancements

Potential improvements for consideration:

1. **Local Wake Word Detection**: Use on-device model (e.g., Porcupine)
2. **Multiple Languages**: Support for non-English commands
3. **Voice Profiles**: Different settings per user
4. **Audio Level Meter**: Visual feedback in overlay
5. **Recording History**: Save and replay commands
6. **Offline Mode**: Cache responses for common commands

---

## 📝 License

Same as the main project (see main README)

---

## 🙏 Credits

Enhanced by Claude Code based on the original [claude-computer-use-macos](https://github.com/PallavAg/claude-computer-use-macos) project.
