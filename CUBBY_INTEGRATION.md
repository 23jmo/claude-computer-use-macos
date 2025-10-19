# Cubby Integration

## Overview

Cubby has been integrated as an MCP tool to give Claude memory and context from your screen history. Claude can now search through OCR text from previous screenshots to recall past conversations, websites, documents, and any visual information.

## Setup

### 1. Install Cubby

```bash
curl -s https://get.cubby.sh/cli | sh
```

This installs the Cubby binary and starts recording your screen in the background. All data stays local in `~/.cubby/`.

### 2. Install Python Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

This installs `httpx` which is needed for the Cubby integration.

### 3. Environment Variables (Optional)

Add to your `.env` file (for documentation purposes, not required for local usage):

```bash
CUBBY_CLIENT_ID=your_client_id
CUBBY_CLIENT_SECRET=your_client_secret
```

**Note:** The local Cubby server (`localhost:3030`) doesn't require authentication. These credentials are only needed if you want to use the remote Cubby API.

## How It Works

### The Tool

The `search_screenshots` tool is automatically available to Claude in the agent loop. It searches through OCR text from your screen history.

**Parameters:**

- `query` (required): Search phrase to find in OCR text
- `limit` (optional): Number of results to return (default: 5)

### Automatic Usage

Claude will automatically use `search_screenshots` when:

- You ask about something you saw/read/viewed before
- You reference past conversations, emails, websites, or documents
- You say things like "what did I..." or "find that thing about..."
- The task requires context from previous screen activity

### Examples

**User:** "What was that Slack message about project alpha?"
→ Claude automatically searches screenshots for "project alpha slack"

**User:** "Find the API documentation I was reading earlier"
→ Claude searches for "API documentation"

**User:** "Remember that email from Sarah about the meeting?"
→ Claude searches for "email Sarah meeting"

## Technical Details

### Implementation

- **Tool Class:** `computer_use_demo/tools/cubby.py`
- **API Endpoint:** `http://localhost:3030/search`
- **Content Type:** OCR (text extracted from screenshots)
- **Response Format:** JSON array of search results

### Files Modified

1. `requirements.txt` - Added `httpx>=0.27.0`
2. `computer_use_demo/tools/cubby.py` - New CubbyTool implementation
3. `computer_use_demo/tools/__init__.py` - Export CubbyTool
4. `computer_use_demo/loop.py` - Register tool and update system prompt

### System Prompt

The system prompt includes a `<CUBBY_MEMORY>` section that instructs Claude to:

- Use search_screenshots proactively
- Search before answering questions about past activity
- Treat it as memory for context-aware responses

## Troubleshooting

### "Cannot connect to Cubby server"

Make sure Cubby is running locally:

```bash
# Check if Cubby is running
curl http://localhost:3030/search?q=test&content_type=ocr&limit=1

# If not running, start it
cubby
```

### No Results Found

- Cubby needs time to capture and process screenshots
- The content you're searching for may not have been on screen yet
- Try different search terms

## Future Enhancements

Potential additions (keeping it simple for now):

- Audio transcription search
- Speaker identification
- Frame-specific queries
- Context7 integration for Cubby API documentation
