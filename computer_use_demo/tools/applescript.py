"""
AppleScript tool for macOS automation.
Enables Claude to control macOS applications via AppleScript.
"""

import asyncio
import shlex
from typing import ClassVar, Literal

from anthropic.types.beta import BetaToolUnionParam

from .base import BaseAnthropicTool, CLIResult, ToolError, ToolResult


class AppleScriptTool(BaseAnthropicTool):
    """
    A tool that allows Claude to execute AppleScript commands for macOS automation.
    Supports sending iMessages, controlling apps, and general AppleScript execution.
    """

    name: ClassVar[Literal["applescript"]] = "applescript"
    api_type: ClassVar[Literal["custom"]] = "custom"

    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        action: str,
        contact: str | None = None,
        message: str | None = None,
        script: str | None = None,
        **kwargs
    ) -> ToolResult:
        """
        Execute AppleScript commands.
        
        Args:
            action: The action to perform. Options:
                - "send_imessage": Send an iMessage to a contact
                - "execute_script": Execute arbitrary AppleScript
            contact: Contact identifier (name, phone, or email) for send_imessage
            message: Message text to send for send_imessage
            script: AppleScript code to execute for execute_script
        
        Returns:
            ToolResult with output or error information
        """
        print(f"### Running AppleScript action: {action}")

        if action == "send_imessage":
            return await self._send_imessage(contact, message)
        elif action == "execute_script":
            return await self._execute_script(script)
        else:
            return ToolResult(error=f"Unknown action: {action}. Use 'send_imessage' or 'execute_script'.")

    async def _send_imessage(self, contact: str | None, message: str | None) -> ToolResult:
        """
        Send an iMessage to a contact.
        
        Args:
            contact: Contact identifier (name, phone number, or email)
            message: The message text to send
        
        Returns:
            ToolResult with success/error information
        """
        if not contact:
            return ToolResult(error="Contact identifier is required for send_imessage")
        if not message:
            return ToolResult(error="Message text is required for send_imessage")

        # Build the AppleScript command
        # Escape single quotes in the message and contact
        escaped_message = message.replace("'", "'\"'\"'")
        escaped_contact = contact.replace("'", "'\"'\"'")
        
        applescript = f"""
tell application "Messages"
    set targetService to 1st account whose service type = iMessage
    set targetBuddy to participant "{escaped_contact}" of targetService
    send "{escaped_message}" to targetBuddy
end tell
"""
        
        print(f"Sending iMessage to '{contact}': {message}")
        
        try:
            # Execute the AppleScript
            result = await self._run_osascript(applescript)
            
            if result.error:
                return ToolResult(
                    error=f"Failed to send iMessage: {result.error}",
                    output=result.output
                )
            
            return ToolResult(
                output=f"Successfully sent iMessage to '{contact}': {message}"
            )
        except Exception as e:
            return ToolResult(error=f"Error sending iMessage: {str(e)}")

    async def _execute_script(self, script: str | None) -> ToolResult:
        """
        Execute arbitrary AppleScript code.
        
        Args:
            script: The AppleScript code to execute
        
        Returns:
            ToolResult with script output or error
        """
        if not script:
            return ToolResult(error="Script is required for execute_script action")

        print(f"Executing AppleScript:\n{script}")
        
        try:
            result = await self._run_osascript(script)
            
            if result.error:
                return ToolResult(
                    error=f"AppleScript error: {result.error}",
                    output=result.output
                )
            
            return ToolResult(
                output=result.output if result.output else "AppleScript executed successfully"
            )
        except Exception as e:
            return ToolResult(error=f"Error executing AppleScript: {str(e)}")

    async def _run_osascript(self, script: str) -> CLIResult:
        """
        Run osascript command with the given AppleScript.
        
        Args:
            script: AppleScript code to execute
        
        Returns:
            CLIResult with output and error streams
        """
        # Use osascript to execute the AppleScript
        process = await asyncio.create_subprocess_shell(
            f"osascript -e {shlex.quote(script)}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        # Wait for the process to complete with a timeout
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            process.kill()
            raise ToolError("AppleScript execution timed out after 30 seconds")
        
        # Decode the output
        output = stdout.decode().strip() if stdout else ""
        error = stderr.decode().strip() if stderr else ""
        
        return CLIResult(output=output, error=error)

    def to_params(self) -> BetaToolUnionParam:
        """
        Return the tool parameters for the Anthropic API.
        
        Returns:
            Tool parameter definition
        """
        return {
            "type": "custom",
            "name": self.name,
            "description": (
                "Execute AppleScript commands to control macOS applications. "
                "Can send iMessages, control apps like Safari, Notes, Mail, and more. "
                "Use 'send_imessage' action to send messages, or 'execute_script' for general automation."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["send_imessage", "execute_script"],
                        "description": "The action to perform: 'send_imessage' to send an iMessage, or 'execute_script' to run AppleScript code"
                    },
                    "contact": {
                        "type": "string",
                        "description": "For send_imessage: Contact identifier (name, phone number with country code like +1234567890, or iMessage email)"
                    },
                    "message": {
                        "type": "string",
                        "description": "For send_imessage: The message text to send"
                    },
                    "script": {
                        "type": "string",
                        "description": "For execute_script: The AppleScript code to execute"
                    }
                },
                "required": ["action"]
            }
        }

