# Voice Control Setup Guide

## Overview

Voice control has been successfully integrated into the Claude Computer Use Demo. You can now control Claude using your voice by saying "Claude" followed by your command.

## Architecture

The implementation consists of three main components:

1. **voice_control.py** - Voice listener module that handles audio recording and Whisper transcription
2. **main.py** (refactored) - Exports `run_computer_use()` function that can be called programmatically
3. **voice_main.py** - New entry point for voice-controlled mode

## Setup Instructions

### 1. Install New Dependencies

Run this command to install the required packages:

```bash
pip3.12 install -r requirements.txt
```

New dependencies added:

- `openai>=1.0.0` - For Whisper API transcription
- `sounddevice>=0.4.6` - For microphone audio recording
- `numpy>=1.24.0` - Required by sounddevice
- `scipy>=1.11.0` - For audio file operations

### 2. Set OpenAI API Key

In addition to your Anthropic API key, you now need an OpenAI API key for Whisper:

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

Get your OpenAI API key here: https://platform.openai.com/api-keys

### 3. Grant Microphone Permissions

MacOS will prompt you to grant microphone access the first time you run voice control. Make sure to allow access.

## Usage

### Start Voice Control

```bash
python3.12 voice_main.py
```

### How to Use

1. The system will start listening continuously
2. Say "Claude" followed by your command, for example:
   - "Claude, save an image of a cat to the desktop"
   - "Claude, open Safari and search for Python tutorials"
   - "Claude, create a new folder called Projects"
3. The system transcribes your command and executes it
4. After completion, it automatically returns to listening mode
5. Press Ctrl+C to stop

### Example Commands

- "Claude, take a screenshot"
- "Claude, open the calculator app"
- "Claude, search Google for AI news"
- "Claude, create a text file with the current date"

## How It Works

1. **Continuous Recording**: Records 5-second audio chunks from your microphone
2. **Transcription**: Sends audio to OpenAI Whisper API for speech-to-text
3. **Wake Word Detection**: Checks if "claude" is mentioned (case-insensitive)
4. **Command Extraction**: Extracts the instruction after "claude"
5. **Execution**: Passes the command to Claude Computer Use
6. **Loop**: Returns to listening after command completes

## Troubleshooting

### "No audio input device found"

- Check that your microphone is connected and working
- Run `python -c "import sounddevice; sounddevice.query_devices()"` to see available devices

### "OpenAI API key not set"

- Make sure you've exported OPENAI_API_KEY environment variable
- Verify the key is valid at https://platform.openai.com/api-keys

### Wake word not detected

- Speak clearly and say "Claude" distinctly
- Make sure you're speaking within the 5-second recording window
- Try saying the full command in one go without long pauses

### High latency

- This is expected - transcription takes 1-3 seconds per chunk
- Local Whisper models would be faster but require more setup

## Cost Considerations

- Whisper API costs $0.006 per minute of audio
- 5-second chunks = ~$0.0005 per transcription
- Continuous listening can add up, but typically stays under $0.50/hour

## Backward Compatibility

The original CLI mode still works exactly as before:

```bash
python3.12 main.py 'your command here'
```

All existing functionality is preserved.
