#!/usr/bin/env python3
"""
STB Tester CLI - AI-Powered Set-Top Box Testing

A standalone CLI tool using Claude Agent SDK that provides an AI assistant
for controlling STB Tester devices, navigating UIs, and generating test cases.

Uses your Claude Code subscription - no separate API key needed!

Usage:
    python -m stb_tester_cli
    # or after install:
    stb-tester-ai
"""

import asyncio
import os
import re
import sys
from pathlib import Path

# Determine paths
CLI_DIR = Path(__file__).parent
PROJECT_DIR = CLI_DIR.parent
MCP_SERVER_PATH = PROJECT_DIR / "mcp_server" / "stb_tester_server.py"


# ============================================================================
# ANSI Color Codes for Dark Theme
# ============================================================================
class Colors:
    # Reset
    RESET = "\033[0m"

    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_BLACK = "\033[48;5;232m"  # Very dark gray (near black)
    BG_DARK = "\033[48;5;235m"   # Dark gray
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Clear screen and set dark background
    CLEAR = "\033[2J\033[H"

    # Set entire screen background (some terminals support this)
    SET_BG_DARK = "\033]11;#1a1a2e\007"  # Dark blue-ish background

    # Theme colors
    BANNER = BRIGHT_CYAN
    TITLE = BRIGHT_WHITE + BOLD
    SUCCESS = BRIGHT_GREEN
    WARNING = BRIGHT_YELLOW
    ERROR = BRIGHT_RED
    INFO = BRIGHT_BLUE
    PROMPT = BRIGHT_MAGENTA + BOLD
    ASSISTANT = BRIGHT_CYAN
    TOOL = BRIGHT_YELLOW
    TOOL_SUCCESS = BRIGHT_GREEN
    MUTED = BRIGHT_BLACK


def set_dark_mode():
    """Try to set terminal to dark mode."""
    C = Colors

    # Clear screen
    print(C.CLEAR, end="")

    # Try multiple methods to set dark background
    # Method 1: OSC 11 - Set background color (works in iTerm2, some xterm, etc.)
    print("\033]11;rgb:1a/1a/2e\007", end="")

    # Method 2: OSC 4 - Set color palette (some terminals)
    # Set color 0 (black) to dark background
    print("\033]4;0;rgb:1a/1a/2e\007", end="")

    # Method 3: For terminals that support it, set foreground to white
    print("\033]10;rgb:ff/ff/ff\007", end="")

    sys.stdout.flush()

    # Also use AppleScript for macOS Terminal (runs in background, won't affect if not macOS Terminal)
    if sys.platform == 'darwin':
        try:
            import subprocess
            # Try to set macOS Terminal to dark background
            applescript = '''
            tell application "Terminal"
                set background color of selected tab of front window to {6682, 6682, 11822}
                set normal text color of selected tab of front window to {65535, 65535, 65535}
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], capture_output=True, timeout=2)
        except:
            pass  # Silently fail if not in macOS Terminal


def print_banner():
    """Print the CLI banner with colors."""
    C = Colors
    print(f"""
{C.BANNER}╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   {C.BRIGHT_GREEN}███████╗████████╗██████╗ {C.BANNER}     {C.BRIGHT_MAGENTA}████████╗███████╗███████╗████████╗{C.BANNER}  ║
║   {C.BRIGHT_GREEN}██╔════╝╚══██╔══╝██╔══██╗{C.BANNER}     {C.BRIGHT_MAGENTA}╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝{C.BANNER}  ║
║   {C.BRIGHT_GREEN}███████╗   ██║   ██████╔╝{C.BANNER}        {C.BRIGHT_MAGENTA}██║   █████╗  ███████╗   ██║   {C.BANNER}  ║
║   {C.BRIGHT_GREEN}╚════██║   ██║   ██╔══██╗{C.BANNER}        {C.BRIGHT_MAGENTA}██║   ██╔══╝  ╚════██║   ██║   {C.BANNER}  ║
║   {C.BRIGHT_GREEN}███████║   ██║   ██████╔╝{C.BANNER}        {C.BRIGHT_MAGENTA}██║   ███████╗███████║   ██║   {C.BANNER}  ║
║   {C.BRIGHT_GREEN}╚══════╝   ╚═╝   ╚═════╝ {C.BANNER}        {C.BRIGHT_MAGENTA}╚═╝   ╚══════╝╚══════╝   ╚═╝   {C.BANNER}  ║
║                                                                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║         {C.TITLE}🎬 AI-Powered Set-Top Box Testing CLI{C.BANNER}                  ║
║              {C.MUTED}Powered by Claude Agent SDK{C.BANNER}                        ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝{C.RESET}
""")


def print_help():
    """Print help information with colors."""
    C = Colors
    print(f"""
{C.DIM}╭──────────────────────────────────────────────────────────────────╮{C.RESET}
{C.DIM}│{C.RESET}  {C.TITLE}📖 Help{C.RESET}                                                       {C.DIM}│{C.RESET}
{C.DIM}╰──────────────────────────────────────────────────────────────────╯{C.RESET}

  {C.BRIGHT_WHITE}Type natural language commands to control your STB device.{C.RESET}

{C.BRIGHT_YELLOW}  ━━━ Examples ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}

  {C.BRIGHT_GREEN}▸{C.RESET} {C.BRIGHT_WHITE}"List available devices"{C.RESET}
  {C.BRIGHT_GREEN}▸{C.RESET} {C.BRIGHT_WHITE}"Connect to stb-tester-48b02d5b0ab7"{C.RESET}
  {C.BRIGHT_GREEN}▸{C.RESET} {C.BRIGHT_WHITE}"Take a screenshot"{C.RESET}
  {C.BRIGHT_GREEN}▸{C.RESET} {C.BRIGHT_WHITE}"Press the HOME key"{C.RESET}
  {C.BRIGHT_GREEN}▸{C.RESET} {C.BRIGHT_WHITE}"Navigate down 3 times then press OK"{C.RESET}
  {C.BRIGHT_GREEN}▸{C.RESET} {C.BRIGHT_WHITE}"Create a test for navigating to EPG"{C.RESET}

{C.BRIGHT_CYAN}  ━━━ Commands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}

  {C.BRIGHT_CYAN}/help{C.RESET}     {C.MUTED}Show this help{C.RESET}
  {C.BRIGHT_CYAN}/status{C.RESET}   {C.MUTED}Show connection status{C.RESET}
  {C.BRIGHT_CYAN}/clear{C.RESET}    {C.MUTED}Clear screen{C.RESET}
  {C.BRIGHT_CYAN}/quit{C.RESET}     {C.MUTED}Exit the CLI{C.RESET}

{C.BRIGHT_MAGENTA}  ━━━ Remote Keys ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}

  {C.MUTED}Navigation:{C.RESET} KEY_UP  KEY_DOWN  KEY_LEFT  KEY_RIGHT  KEY_OK  KEY_BACK
  {C.MUTED}Actions:{C.RESET}    KEY_HOME  KEY_EPG  KEY_MENU  KEY_INFO
  {C.MUTED}Playback:{C.RESET}   KEY_PLAY  KEY_PAUSE  KEY_STOP
  {C.MUTED}Colors:{C.RESET}     KEY_RED  KEY_GREEN  KEY_YELLOW  KEY_BLUE
""")


def print_status():
    """Print current connection status with colors."""
    C = Colors
    portal_url = os.environ.get("STBT_PORTAL_URL", "")
    portal_token = os.environ.get("STBT_PORTAL_TOKEN", "")
    device_id = os.environ.get("STBT_DEVICE_ID", "")

    print(f"""
{C.DIM}┌──────────────────────────────────────────────────────────────┐{C.RESET}
{C.DIM}│{C.RESET}  {C.TITLE}📊 Connection Status{C.RESET}                                       {C.DIM}│{C.RESET}
{C.DIM}├──────────────────────────────────────────────────────────────┤{C.RESET}""")

    # Portal URL
    if portal_url:
        print(f"{C.DIM}│{C.RESET}  {C.BRIGHT_WHITE}Portal URL    :{C.RESET}  {C.SUCCESS}✓ {portal_url}{C.RESET}")
    else:
        print(f"{C.DIM}│{C.RESET}  {C.BRIGHT_WHITE}Portal URL    :{C.RESET}  {C.WARNING}✗ Not configured{C.RESET}")

    # Token
    if portal_token:
        print(f"{C.DIM}│{C.RESET}  {C.BRIGHT_WHITE}Portal Token  :{C.RESET}  {C.SUCCESS}✓ ***{portal_token[-4:]}{C.RESET}")
    else:
        print(f"{C.DIM}│{C.RESET}  {C.BRIGHT_WHITE}Portal Token  :{C.RESET}  {C.WARNING}✗ Not configured{C.RESET}")

    # Device
    if device_id:
        print(f"{C.DIM}│{C.RESET}  {C.BRIGHT_WHITE}Default Device:{C.RESET}  {C.BRIGHT_CYAN}{device_id}{C.RESET}")
    else:
        print(f"{C.DIM}│{C.RESET}  {C.BRIGHT_WHITE}Default Device:{C.RESET}  {C.MUTED}None{C.RESET}")

    print(f"{C.DIM}│{C.RESET}  {C.BRIGHT_WHITE}MCP Server    :{C.RESET}  {C.INFO}{MCP_SERVER_PATH.name}{C.RESET}")

    print(f"""{C.DIM}└──────────────────────────────────────────────────────────────┘{C.RESET}
""")


SYSTEM_PROMPT = """You are an AI assistant for STB Tester - a tool for automated testing of Set-Top Boxes and Smart TVs.

You have access to STB Tester MCP tools that let you:
1. List and connect to STB Tester devices (stb_list_devices, stb_connect_device)
2. Take screenshots from the device (stb_device_screenshot)
3. Send remote control key presses (stb_device_press)
4. Get device information (stb_device_info)
5. Run tests on devices (stb_run_test)

When the user asks you to:
- Navigate somewhere: Use stb_device_press to send key presses (KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK, KEY_HOME, KEY_EPG)
- See what's on screen: Use stb_device_screenshot to capture the display
- Create a test: Write pytest-compatible test scripts using stbt_core
- Connect to a device: Use stb_connect_device with the device ID

Common remote control keys:
- Navigation: KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK
- Actions: KEY_HOME, KEY_EPG, KEY_MENU, KEY_INFO
- Playback: KEY_PLAY, KEY_PAUSE, KEY_STOP, KEY_FASTFORWARD, KEY_REWIND
- Numbers: KEY_0 through KEY_9
- Colors: KEY_RED, KEY_GREEN, KEY_YELLOW, KEY_BLUE

Always be helpful and explain what you're doing. When generating tests, follow pytest conventions and STB Tester best practices.

For test scripts, use this pattern:
```python
import stbt_core as stbt

def test_example():
    stbt.press("KEY_HOME")
    stbt.wait_for_match("reference_image.png", timeout_secs=10)
    stbt.press("KEY_OK")
```"""


async def process_query(prompt: str, options) -> str:
    """Process a single query and return the response."""
    from claude_agent_sdk import query
    C = Colors

    response_parts = []
    tool_count = 0
    last_was_tool = False

    async for message in query(prompt=prompt, options=options):
        msg_type = type(message).__name__

        if msg_type == 'AssistantMessage':
            # AssistantMessage has content which is a list of TextBlock/ToolUseBlock
            if hasattr(message, 'content') and message.content:
                for block in message.content:
                    block_type = type(block).__name__

                    if block_type == 'TextBlock' and hasattr(block, 'text'):
                        text = block.text

                        # Add newline after tools for separation
                        if last_was_tool:
                            print(f"\n", flush=True)
                            last_was_tool = False

                        # Format the text for better readability
                        formatted_text = format_response_text(text, C)
                        print(formatted_text, end="", flush=True)
                        response_parts.append(text)

                    elif block_type == 'ToolUseBlock':
                        tool_name = getattr(block, 'name', 'tool')
                        tool_count += 1
                        # Clean tool name display
                        display_name = tool_name.replace('mcp__stb-tester__', '').replace('_', ' ').title()
                        print(f"\n\n   {C.BG_DARK}{C.TOOL} ⚡ {display_name} {C.RESET}", end="", flush=True)
                        last_was_tool = True

        elif msg_type == 'ResultMessage':
            # End of response
            if hasattr(message, 'is_error') and message.is_error:
                error = getattr(message, 'result', 'Unknown error')
                print(f"\n\n   {C.ERROR}❌ Error: {error}{C.RESET}", flush=True)

    return "".join(response_parts)


def format_response_text(text: str, C) -> str:
    """Format response text for better readability."""
    lines = text.split('\n')
    formatted_lines = []
    in_code_block = False

    for line in lines:
        # Detect code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            if in_code_block:
                formatted_lines.append(f"\n{C.DIM}{'─' * 50}{C.RESET}")
                formatted_lines.append(f"{C.MUTED}{line}{C.RESET}")
            else:
                formatted_lines.append(f"{C.MUTED}{line}{C.RESET}")
                formatted_lines.append(f"{C.DIM}{'─' * 50}{C.RESET}\n")
            continue

        if in_code_block:
            # Code in cyan
            formatted_lines.append(f"{C.BRIGHT_CYAN}  {line}{C.RESET}")
        elif line.startswith('## '):
            # Headers in bold yellow
            formatted_lines.append(f"\n{C.BRIGHT_YELLOW}{C.BOLD}{line}{C.RESET}\n")
        elif line.startswith('### '):
            # Sub-headers in yellow
            formatted_lines.append(f"\n{C.YELLOW}{line}{C.RESET}")
        elif line.startswith('# '):
            # Main headers in bold white
            formatted_lines.append(f"\n{C.TITLE}{line}{C.RESET}\n")
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            # Bullet points with green bullets
            bullet_content = line.strip()[2:]
            indent = len(line) - len(line.lstrip())
            formatted_lines.append(f"{' ' * indent}{C.BRIGHT_GREEN}●{C.RESET} {C.BRIGHT_WHITE}{bullet_content}{C.RESET}")
        elif line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
            # Numbered lists in cyan
            formatted_lines.append(f"{C.BRIGHT_CYAN}{line}{C.RESET}")
        elif '|' in line and line.strip().startswith('|'):
            # Table formatting
            formatted_lines.append(f"{C.DIM}{line}{C.RESET}")
        elif line.strip().startswith('**') and line.strip().endswith('**'):
            # Bold text
            content = line.strip()[2:-2]
            formatted_lines.append(f"{C.BOLD}{C.BRIGHT_WHITE}{content}{C.RESET}")
        elif '`' in line:
            # Inline code highlighting
            formatted = re.sub(r'`([^`]+)`', f'{C.BRIGHT_CYAN}`\\1`{C.BRIGHT_WHITE}', line)
            formatted_lines.append(f"{C.BRIGHT_WHITE}{formatted}{C.RESET}")
        else:
            # Regular text
            formatted_lines.append(f"{C.BRIGHT_WHITE}{line}{C.RESET}")

    return '\n'.join(formatted_lines)


async def run_cli():
    """Run the interactive CLI."""
    try:
        from claude_agent_sdk import ClaudeAgentOptions
        from claude_agent_sdk.types import McpStdioServerConfig
    except ImportError:
        print("Error: Claude Agent SDK not installed.")
        print("Install with: pip install claude-agent-sdk")
        sys.exit(1)

    C = Colors

    # Set dark mode background
    set_dark_mode()

    print_banner()

    # Check configuration
    portal_url = os.environ.get("STBT_PORTAL_URL", "")
    portal_token = os.environ.get("STBT_PORTAL_TOKEN", "")

    # Status box
    print(f"{C.DIM}┌────────────────────────────────────────────────────────────┐{C.RESET}")

    if portal_url and portal_token:
        print(f"{C.DIM}│{C.RESET}  {C.SUCCESS}✓{C.RESET} Portal: {C.INFO}{portal_url[:45]}{C.RESET}")
    else:
        print(f"{C.DIM}│{C.RESET}  {C.WARNING}✗{C.RESET} Portal not configured")

    # Configure MCP server for STB Tester
    mcp_servers = {}
    if MCP_SERVER_PATH.exists():
        mcp_servers["stb-tester"] = McpStdioServerConfig(
            type="stdio",
            command="python3",
            args=[str(MCP_SERVER_PATH)],
            env={
                "STBT_PORTAL_URL": portal_url,
                "STBT_PORTAL_TOKEN": portal_token,
                "PYTHONPATH": str(PROJECT_DIR),
            }
        )
        print(f"{C.DIM}│{C.RESET}  {C.SUCCESS}✓{C.RESET} MCP Server: {C.INFO}{MCP_SERVER_PATH.name}{C.RESET}")
    else:
        print(f"{C.DIM}│{C.RESET}  {C.WARNING}✗{C.RESET} MCP Server not found")

    print(f"{C.DIM}│{C.RESET}  {C.SUCCESS}✓{C.RESET} Auth: {C.MUTED}Using Claude Code subscription{C.RESET}")
    print(f"{C.DIM}└────────────────────────────────────────────────────────────┘{C.RESET}")

    print(f"\n  {C.MUTED}Type{C.RESET} {C.BRIGHT_CYAN}/help{C.RESET} {C.MUTED}for commands, or just start chatting!{C.RESET}\n")

    # Create options - reused for each query
    # bypassPermissions allows all tool usage without prompting
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers=mcp_servers,
        permission_mode="bypassPermissions",
        cwd=str(PROJECT_DIR),
    )

    # Main interaction loop
    while True:
        try:
            user_input = input(f"\n{C.PROMPT}🎮 You ▶{C.RESET}  ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.startswith("/"):
                cmd = user_input.lower()
                if cmd in ["/quit", "/exit", "/q"]:
                    print(f"\n{C.SUCCESS}👋 Goodbye!{C.RESET}")
                    break
                elif cmd == "/help":
                    print_help()
                    continue
                elif cmd == "/status":
                    print_status()
                    continue
                elif cmd == "/clear":
                    set_dark_mode()
                    print_banner()
                    continue
                else:
                    print(f"{C.WARNING}Unknown command:{C.RESET} {user_input}")
                    continue

            # Visual separator
            print(f"\n{C.DIM}{'─' * 60}{C.RESET}")
            print(f"{C.ASSISTANT}{C.BOLD}🤖 Assistant:{C.RESET}\n", flush=True)

            # Process the query
            try:
                await process_query(user_input, options)
            except Exception as query_error:
                print(f"\n{C.ERROR}❌ Query error: {query_error}{C.RESET}")
                import traceback
                traceback.print_exc()

            # End separator
            print(f"\n{C.DIM}{'─' * 60}{C.RESET}")

        except KeyboardInterrupt:
            print(f"\n\n{C.SUCCESS}👋 Goodbye!{C.RESET}")
            break
        except Exception as e:
            print(f"\n{C.ERROR}❌ Error: {e}{C.RESET}")
            import traceback
            traceback.print_exc()
            continue


def main():
    """Main entry point."""
    asyncio.run(run_cli())


if __name__ == "__main__":
    main()
