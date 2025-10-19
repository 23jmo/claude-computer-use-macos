#!/usr/bin/env python3
"""
Test script for Cubby integration.
Demonstrates how Claude can search through screen history.
"""

import asyncio
import os
import dotenv
from main import run_computer_use

dotenv.load_dotenv()


async def test_cubby_search():
    """Test Cubby search integration with Claude."""
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Error: Please set ANTHROPIC_API_KEY in your .env file")
        return
    
    print("=" * 60)
    print("Cubby Integration Test")
    print("=" * 60)
    print("\nThis will test Claude's ability to search through screen history.")
    print("Make sure Cubby is running locally (http://localhost:3030)\n")
    
    # Test instruction that should trigger Cubby search
    instruction = "Search my screen history for anything about 'python' and tell me what you find."
    
    print(f"Instruction: {instruction}\n")
    print("Claude should automatically use the search_screenshots tool...\n")
    
    # Run Claude with the instruction
    await run_computer_use(
        instruction=instruction,
        api_key=api_key,
        enable_websocket=False
    )
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_cubby_search())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")

