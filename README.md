# Claude Computer Use Demo for MacOS

This repository contains a Python script that demonstrates Anthropic's Computer Use capabilities, modified to run on MacOS without requiring a Docker container. The script allows Claude 3.5 Sonnet to perform tasks on your Mac by simulating mouse and keyboard actions as well as running bash command.

**NEW Features:**

- 🎤 **Voice Control**: Use OpenAI Whisper to control Claude with your voice by saying "Claude" followed by your command
- 📱 **AppleScript Automation**: Claude can now send iMessages, control macOS apps, and automate your system using AppleScript
- 🎨 **Overlay App**: Real-time transparent overlay showing Claude's activity using Electron + React

Forked from Anthropic's [computer use demo](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo) - optimized for MacOS.
View Anthropic's docs [here](https://docs.anthropic.com/en/docs/build-with-claude/computer-use).

> [!WARNING]  
> Use this script with caution. Allowing Claude to control your computer can be risky. By running this script, you assume all responsibility and liability.

## Installation and Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/PallavAg/claude-computer-use-macos.git
   cd claude-computer-use-macos
   ```

2. **Create a virtual environment + install dependencies:**

   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip3.12 install -r requirements.txt
   ```

3. **Set your API keys as environment variables:**

   ```bash
   export ANTHROPIC_API_KEY="CLAUDE_API_KEY"
   export OPENAI_API_KEY="YOUR_OPENAI_KEY"  # Only needed for voice control
   export DEEPGRAM_API_KEY="YOUR_DEEPGRAM_KEY"  # Only needed for text-to-speech
   ```

   Replace `CLAUDE_API_KEY` with your actual Anthropic API key. You find yours [here](https://console.anthropic.com/settings/keys).

   For voice control, also set your OpenAI API key (get it [here](https://platform.openai.com/api-keys)).

   For text-to-speech (speaking Claude's responses), set your Deepgram API key (get it [here](https://console.deepgram.com/)).

4. **Grant Accessibility Permissions:**

   The script uses `pyautogui` to control mouse and keyboard events. On MacOS, you need to grant accessibility permissions. These popups should show automatically the first time you run the script so you can skip this step. But to manually provide permissions:

   - Go to **System Settings** > **Privacy & Security** > **Privacy** tab.
   - Select **Accessibility** from the list on the left.
   - Add your terminal application or Python interpreter to the list of allowed apps.

   For AppleScript automation (iMessage, Notes, etc.):

   - Go to **System Settings** > **Privacy & Security** > **Automation**.
   - Enable permissions for Terminal/Python to control Messages and other apps.

## Usage

### Option 1: Voice Control with Overlay (NEW!)

Run the overlay-enabled version that listens for the wake word "Claude" and displays activity:

**Terminal 1 - Start backend:**

```bash
python3.12 overlay_main.py
```

**Terminal 2 - Start overlay (requires Node.js):**

```bash
cd electron-overlay
npm install  # First time only
npm start
```

A transparent overlay will appear in the top-right corner showing real-time activity. Then simply speak your commands:

- "Claude, save an image of a cat to the desktop"
- "Claude, open Safari and look up Anthropic"
- "Claude, create a new text file called notes.txt"
- "Claude, send an iMessage to John saying hello"
- "Claude, create a note about my meeting tomorrow"

Press `Ctrl+C` in both terminals to stop.

### Option 2: Voice Control (No Overlay)

Run the voice-controlled version without the overlay:

```bash
python3.12 voice_main.py
```

### Option 3: Command Line

You can run the script by passing the instruction directly via the command line:

```bash
python3.12 main.py 'Open Safari and look up Anthropic'
```

Replace `'Open Safari and look up Anthropic'` with your desired instruction.

**Note:** If you do not provide an instruction via the command line, the script will use the default instruction specified in `main.py`.

## Features

### 🎨 Overlay App

A transparent Electron overlay that displays real-time Claude activity:

- **Glassmorphism Design**: Beautiful transparent window with backdrop blur
- **Click-through**: Mouse events pass through to apps below
- **Always On Top**: Stays visible while Claude works
- **Real-time Updates**: Shows instructions, thoughts, tool outputs, and screenshots
- **WebSocket Connection**: Live feed from Python backend

See [electron-overlay/README.md](electron-overlay/README.md) for overlay documentation.

### 🎤 Voice Control

See [VOICE_CONTROL_GUIDE.md](VOICE_CONTROL_GUIDE.md) for detailed voice control documentation.

### 🔊 Text-to-Speech

Claude's responses are automatically spoken aloud in voice and overlay modes using Deepgram's high-quality TTS:

- **Automatic Speech**: AI messages are converted to speech and played in the background
- **Non-blocking**: Speech plays while Claude continues working on tasks
- **High Quality**: Uses Deepgram's "aura-2-asteria-en" voice model
- **Optional**: TTS is disabled if `DEEPGRAM_API_KEY` is not set

### 📱 AppleScript Automation

Claude can now control macOS applications using AppleScript:

- **Send iMessages**: "Send a message to Alice saying hello"
- **Control Notes**: "Create a new note titled 'Ideas'"
- **Manage Calendar**: "Add a meeting to my calendar for tomorrow"
- **Automate Safari**: "Open Safari and search for recipes"
- **And much more!**

See [APPLESCRIPT_GUIDE.md](APPLESCRIPT_GUIDE.md) for comprehensive AppleScript documentation and examples.

## Exiting the Script

You can quit the script at any time by pressing `Ctrl+C` in the terminal.

## ⚠ Disclaimer

> [!CAUTION]
>
> - **Security Risks:** This script allows claude to control your computer's mouse and keyboard and run bash commands. Use it at your own risk.
> - **Responsibility:** By running this script, you assume all responsibility and liability for any results.
