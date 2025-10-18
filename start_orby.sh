#!/bin/bash

# Orby Voice Assistant Startup Script
echo "🚀 Starting Orby Voice Assistant..."
echo ""

# Check if API keys are set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY environment variable not set"
    echo "Please set it with: export ANTHROPIC_API_KEY='your_key_here'"
    exit 1
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable not set"
    echo "Please set it with: export OPENAI_API_KEY='your_key_here'"
    exit 1
fi

echo "✅ API keys found"
echo ""

# Start the API server in the background
echo "🔧 Starting Orby API server..."
python3.12 orby_api_server.py &
API_PID=$!

# Wait a moment for the server to start
sleep 2

# Start the Orby widget
echo "🎨 Starting Orby widget..."
cd cursor-desktop-app
npm start &
WIDGET_PID=$!

echo ""
echo "🎯 Orby Voice Assistant is running!"
echo "📍 Widget: Floating in top-right corner"
echo "🔗 API Server: http://localhost:8000"
echo ""
echo "💡 Usage:"
echo "   1. Click the Orby logo to start listening"
echo "   2. Say 'Orby' followed by your command"
echo "   3. Example: 'Orby, take a screenshot'"
echo ""
echo "Press Ctrl+C to stop both services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Orby services..."
    kill $API_PID 2>/dev/null
    kill $WIDGET_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for either process to exit
wait
