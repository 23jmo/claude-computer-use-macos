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

        print(f"Sending iMessage to '{contact}': {message}")
        
        # First, try to resolve the contact name to a phone/email from Contacts app
        # Check if contact looks like a phone number or email (skip lookup)
        if contact.startswith('+') or '@' in contact or contact.replace('-','').replace(' ','').isdigit():
            # It's already a phone number or email
            target_id = contact
            print(f"Using direct identifier: {target_id}")
        else:
            # Try to look up the contact in Contacts app
            print(f"Looking up contact '{contact}' in Contacts app...")
            lookup_result = await self._lookup_contact(contact)
            if lookup_result.error:
                return ToolResult(
                    error=f"Could not find contact '{contact}': {lookup_result.error}. Try using a phone number like +1234567890 or email address instead.",
                    output=lookup_result.output
                )
            target_id = lookup_result.output.strip() if lookup_result.output else contact
            print(f"Resolved to: {target_id}")
        
        # Clean up phone number formatting - remove parentheses, hyphens, spaces
        # Messages needs clean numbers with country code like +14155551234
        if target_id and not '@' in target_id:
            # It's a phone number, clean it up
            cleaned = target_id.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            
            # Ensure it has a country code (add +1 for US if missing)
            if not cleaned.startswith('+'):
                # If it's a 10-digit number, add +1 for US
                if len(cleaned) == 10 and cleaned.isdigit():
                    cleaned = '+1' + cleaned
                    print(f"Added country code: {target_id} → {cleaned}")
                # If it's 11 digits starting with 1, add +
                elif len(cleaned) == 11 and cleaned.startswith('1') and cleaned.isdigit():
                    cleaned = '+' + cleaned
                    print(f"Added + prefix: {target_id} → {cleaned}")
                else:
                    print(f"Cleaned phone number: {target_id} → {cleaned}")
            else:
                if cleaned != target_id:
                    print(f"Cleaned phone number: {target_id} → {cleaned}")
            
            target_id = cleaned
        
        # Escape quotes and backslashes for AppleScript strings
        # AppleScript uses backslash escaping inside quoted strings
        escaped_message = message.replace('\\', '\\\\').replace('"', '\\"')
        escaped_target = target_id.replace('\\', '\\\\').replace('"', '\\"')
        
        # Build AppleScript - using double quotes with backslash escaping
        applescript = f'tell application "Messages" to send "{escaped_message}" to buddy "{escaped_target}"'
        
        # Print the exact AppleScript command for debugging
        print(f"Exact AppleScript command: {applescript}")
        
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
    
    async def _lookup_contact(self, name: str) -> CLIResult:
        """
        Look up a contact in the Contacts app and return their phone number or email.
        
        Args:
            name: Contact name to search for
        
        Returns:
            CLIResult with phone/email or error
        """
        # Escape the name for AppleScript
        escaped_name = name.replace('\\', '\\\\').replace('"', '\\"')
        
        # Try to find the contact and get their primary phone or email
        applescript = f'''
tell application "Contacts"
    set matchingPeople to people whose name contains "{escaped_name}"
    if (count of matchingPeople) is 0 then
        error "No contact found with name containing '{escaped_name}'"
    end if
    
    set thePerson to item 1 of matchingPeople
    
    -- Try to get phone number first
    if (count of phones of thePerson) > 0 then
        set thePhone to value of first phone of thePerson
        return thePhone
    else if (count of emails of thePerson) > 0 then
        set theEmail to value of first email of thePerson
        return theEmail
    else
        error "Contact found but has no phone number or email address"
    end if
end tell
'''
        
        try:
            return await self._run_osascript(applescript)
        except Exception as e:
            return CLIResult(output="", error=str(e))

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

