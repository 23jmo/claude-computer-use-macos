# AppleScript Automation Guide

This guide explains how to use the AppleScript automation capabilities integrated into Claude Computer Use.

## Overview

Claude can now control macOS applications directly using AppleScript. This enables powerful automation including:

- Sending iMessages
- Controlling Safari, Notes, Mail, and other apps
- Creating calendar events and reminders
- Managing files with Finder
- And much more!

## Features

### 1. Send iMessages

Claude can send iMessages to your contacts automatically.

**Example voice commands:**

- "Claude, send an iMessage to John saying hello"
- "Claude, message mom that I'll be home late"
- "Claude, text +14155551234 the meeting notes"

**Example CLI usage:**

```bash
python main.py "Send an iMessage to Alice saying 'Meeting at 3pm'"
```

**Direct tool usage:**

```python
await applescript_tool(
    action="send_imessage",
    contact="John Smith",  # or phone number or email
    message="Hello from Claude!"
)
```

### 2. Execute AppleScript

Run any AppleScript command to control macOS applications.

**Example voice commands:**

- "Claude, create a new note in Notes app with the title 'Ideas'"
- "Claude, open Safari and navigate to google.com"
- "Claude, set a reminder for tomorrow at 9am"

**Example CLI usage:**

```bash
python main.py "Create a new note titled 'Shopping List'"
```

**Direct tool usage:**

```python
await applescript_tool(
    action="execute_script",
    script='''
    tell application "Notes"
        make new note with properties {name:"My Note", body:"Content here"}
    end tell
    '''
)
```

## Supported Applications

The following macOS applications have good AppleScript support:

- **Messages**: Send iMessages and SMS
- **Notes**: Create and manage notes
- **Safari**: Control web browsing
- **Mail**: Send and manage emails
- **Calendar**: Create events
- **Reminders**: Set reminders
- **Finder**: File management
- **Music**: Control playback
- **System Events**: System-level automation
- **And many more!**

## Contact Identifiers for iMessage

When sending iMessages, you can specify the contact in three ways:

1. **By name**: `"John Smith"` (as it appears in Contacts)
2. **By phone**: `"+14155551234"` (with country code)
3. **By email**: `"john@example.com"` (iMessage-enabled email)

## AppleScript Examples

### Create a Calendar Event

```applescript
tell application "Calendar"
    tell calendar "Home"
        make new event with properties {summary:"Meeting", start date:(current date) + 1 * days}
    end tell
end tell
```

### Open URL in Safari

```applescript
tell application "Safari"
    activate
    open location "https://www.example.com"
end tell
```

### Create a Reminder

```applescript
tell application "Reminders"
    make new reminder with properties {name:"Call dentist", due date:(current date) + 1 * days}
end tell
```

### Get Current Song in Music

```applescript
tell application "Music"
    if player state is playing then
        return name of current track
    end if
end tell
```

## System Prompt Behavior

The system prompt has been modified to give Claude full permission to execute automation commands:

- **No confirmation required**: Claude will execute commands immediately
- **Direct action**: No safety warnings about accessing personal data
- **Autonomous operation**: Claude decides when to use AppleScript vs bash

This is intentional for local automation. Claude operates with your user permissions.

## Security Considerations

- AppleScript runs with your user permissions (no sudo/elevation)
- Only affects your local machine
- Cannot access files outside your user directory without permission
- You can interrupt with Ctrl+C at any time
- All actions are logged to console

## Testing

Run the test script to verify the integration:

```bash
python test_applescript.py
```

This will:

1. Initialize the AppleScript tool
2. Generate tool parameters
3. Execute a simple test dialog

## Troubleshooting

### "Messages not authorized"

Grant accessibility permissions:

1. System Settings → Privacy & Security → Automation
2. Enable permissions for Terminal/Python to control Messages

### "Contact not found"

- Verify the contact exists in Messages app
- Try using phone number with country code: `+1234567890`
- Ensure iMessage is set up and signed in

### "AppleScript execution timed out"

- Script took longer than 30 seconds
- Check for infinite loops or user interaction prompts
- Simplify the script

### Script errors

- Verify AppleScript syntax
- Test the script in Script Editor first
- Check app-specific documentation

## Voice Control Integration

When using voice control mode:

```bash
python voice_main.py
```

Simply say:

- "Claude, send a message to [contact] saying [message]"
- "Claude, create a note about [topic]"
- "Claude, open [application]"

Claude will understand the intent and use the appropriate tool (AppleScript, bash, or computer control).

## Advanced Usage

### Chaining Commands

You can ask Claude to perform multiple actions:

```bash
python main.py "Send iMessage to John saying 'Check your email' and create a reminder to follow up tomorrow"
```

### Conditional Logic

Claude can make decisions:

```bash
python main.py "If Safari is running, close it. Otherwise open it."
```

### Data Processing

Combine with other tools:

```bash
python main.py "Read the file notes.txt and send its contents via iMessage to Alice"
```

## API Reference

### AppleScriptTool

```python
class AppleScriptTool(BaseAnthropicTool):
    async def __call__(
        action: str,           # "send_imessage" or "execute_script"
        contact: str | None,   # For send_imessage
        message: str | None,   # For send_imessage
        script: str | None,    # For execute_script
    ) -> ToolResult
```

### Tool Parameters

```json
{
  "type": "custom",
  "name": "applescript",
  "description": "Execute AppleScript commands to control macOS applications...",
  "input_schema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["send_imessage", "execute_script"]
      },
      "contact": { "type": "string" },
      "message": { "type": "string" },
      "script": { "type": "string" }
    },
    "required": ["action"]
  }
}
```

## Resources

- [AppleScript Language Guide](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/)
- [Mac Automation Scripting Guide](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/)
- Application-specific AppleScript dictionaries (File → Open Dictionary in Script Editor)

## Contributing

To extend AppleScript capabilities:

1. Add new helper methods to `AppleScriptTool` class
2. Update the tool's input schema
3. Add examples to this guide
4. Test thoroughly on macOS

## License

Same as the main project license.
