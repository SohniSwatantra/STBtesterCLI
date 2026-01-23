# STB Tester AI CLI

An AI-powered command-line interface for STB Tester, built with Claude Agent SDK.

## Features

- 🤖 **Natural Language Control** - Talk to your STB device naturally
- 📺 **Device Management** - List, connect, and control STB Tester nodes
- 📸 **Screenshots** - Capture and analyze device screens
- 🎮 **Remote Control** - Send key presses and navigate menus
- 🧪 **Test Generation** - Automatically generate pytest test scripts
- 🚀 **Test Execution** - Run tests directly on devices

## Installation

```bash
# Install from the stb-tester-main directory
cd stb_tester_cli
pip install -e .

# Or install dependencies directly
pip install claude-agent-sdk
```

## Configuration

Set environment variables for your STB Tester Portal:

```bash
export STBT_PORTAL_URL="https://your-company.stb-tester.com"
export STBT_PORTAL_TOKEN="your-api-token"
export STBT_DEVICE_ID="stb-tester-node-001"  # Optional default device
```

## Usage

### Start the CLI

```bash
# Run as module
python -m stb_tester_cli

# Or after installation
stb-tester-ai
```

### Example Interactions

```
🎮 You: List available devices

🤖 Assistant: I'll list the available STB Tester devices for you.
   [Using list_devices...] Done.

   Found 3 devices:
   - stb-tester-001 (EOSv2_PROD) - Online, Available
   - stb-tester-002 (EOSv1_PROD) - Online, Available
   - stb-tester-003 (Test Node) - Offline

🎮 You: Connect to stb-tester-001

🤖 Assistant: Connected to stb-tester-001 (EOSv2_PROD).
   The device is online and available.

🎮 You: Take a screenshot

🤖 Assistant: I've captured a screenshot from the device.
   Saved to: screenshots/screenshot_20260123_101530.png

🎮 You: Navigate to the Movies section

🤖 Assistant: I'll navigate to the Movies section. Let me press the
   necessary keys...
   [Using press_key: KEY_HOME...] Done.
   [Using navigate_to: right, 2 steps...] Done.
   [Using press_key: KEY_OK...] Done.

   I've navigated to what should be the Movies section.

🎮 You: Create a test for navigating to Movies from Home

🤖 Assistant: I'll generate a test script for this navigation flow.
   [Using generate_test_script...] Done.

   Created test file: stb_tests/test_navigate_to_movies.py
```

### Special Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help information |
| `/status` | Show connection status |
| `/clear` | Clear the screen |
| `/quit` | Exit the CLI |

## Available Tools

The AI assistant has access to these tools:

| Tool | Description |
|------|-------------|
| `list_devices` | List available STB Tester nodes |
| `connect_device` | Connect to a specific device |
| `get_device_info` | Get device details |
| `take_screenshot` | Capture device screen |
| `press_key` | Send a remote control key |
| `press_keys` | Send multiple keys in sequence |
| `navigate_to` | Navigate in a direction |
| `generate_test_script` | Create pytest test files |
| `run_test` | Execute tests on device |
| `get_job_status` | Check test job status |

## Common Remote Control Keys

- **Navigation**: KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_OK, KEY_BACK
- **Actions**: KEY_HOME, KEY_EPG, KEY_MENU, KEY_INFO
- **Playback**: KEY_PLAY, KEY_PAUSE, KEY_STOP, KEY_FASTFORWARD, KEY_REWIND
- **Numbers**: KEY_0 through KEY_9
- **Colors**: KEY_RED, KEY_GREEN, KEY_YELLOW, KEY_BLUE

## Requirements

- Python 3.10+
- Claude Agent SDK
- STB Tester Portal account (for device control)
- Claude Code authentication or Anthropic API key

## License

MIT License
