"""Cubby tool for searching OCR screenshots."""

import httpx
from anthropic.types.beta import BetaToolUnionParam

from .base import BaseAnthropicTool, ToolResult


class CubbyTool(BaseAnthropicTool):
    """
    Tool for searching through OCR screenshots using local Cubby server.
    Provides memory and context from previously viewed screen content.
    """

    def to_params(self) -> BetaToolUnionParam:
        return {
            "name": "search_screenshots",
            "description": "Search through OCR text from previous screenshots to find content you've seen on screen before. Use this to recall past conversations, websites, documents, or any visual information from screen history. This is your memory - use it proactively when the user asks about something they saw before.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search phrase to find in OCR text from screenshots (e.g., 'project alpha', 'slack messages', 'API documentation')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        }

    async def __call__(self, query: str, limit: int = 5, **kwargs):
        """
        Search Cubby for OCR screenshot content.
        
        Args:
            query: Search phrase to find in OCR text
            limit: Number of results to return (default: 5)
        """
        try:
            # Make request to local Cubby server
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "http://localhost:3030/search",
                    params={
                        "q": query,
                        "content_type": "ocr",
                        "limit": limit,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                response_data = response.json()
                
            # Extract the data array from Cubby response
            results = response_data.get("data", [])

            # Format results as readable text
            if not results or len(results) == 0:
                return ToolResult(
                    output=f"No screenshots found matching '{query}'. The content may not have been captured yet."
                )

            # Format OCR results with context
            output_lines = [f"Found {len(results)} screenshot(s) matching '{query}':\n"]
            for i, result in enumerate(results, 1):
                content = result.get("content", {})
                ocr_text = content.get("text", "")
                app_name = content.get("app_name", "Unknown")
                window_name = content.get("window_name", "")
                timestamp = content.get("timestamp", "")
                
                # Truncate long OCR text for readability
                if len(ocr_text) > 300:
                    ocr_text = ocr_text[:300] + "..."
                
                output_lines.append(f"\n{i}. [{app_name}] {window_name}")
                output_lines.append(f"   Time: {timestamp}")
                output_lines.append(f"   Text: {ocr_text}")

            return ToolResult(output="\n".join(output_lines))

        except httpx.TimeoutException:
            return ToolResult(
                error="Cubby server timeout. Make sure Cubby is running locally (http://localhost:3030)"
            )
        except httpx.ConnectError:
            return ToolResult(
                error="Cannot connect to Cubby server. Make sure Cubby is running locally (http://localhost:3030)"
            )
        except Exception as e:
            return ToolResult(error=f"Cubby search failed: {str(e)}")

