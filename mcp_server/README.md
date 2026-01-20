# STB Tester MCP Server

A Model Context Protocol (MCP) server that exposes STB Tester APIs as tools. This allows Claude Code, Claude Desktop, and other MCP-compatible clients to control set-top boxes and perform automated testing.

## Features

- **Remote Device Control**: Connect to real STB Tester nodes by device ID via Portal API
- **Local Control**: Direct control when running on STB Tester hardware
- **Remote Control**: Press keys, navigate menus, control playback
- **Image Matching**: Find and verify UI elements using reference images
- **Motion Detection**: Verify video playback
- **OCR**: Read text from the screen
- **Screenshots**: Capture and analyze video frames from real devices

## Installation

### Prerequisites

- Python 3.10 or later
- MCP SDK: `pip install mcp`
- STB Tester (optional, runs in mock mode without it)

### Install the MCP Server

```bash
cd mcp_server
pip install -e .
```

Or install with STB Tester support:

```bash
pip install -e ".[stbt]"
```

## Configuration

### Claude Desktop

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stb-tester": {
      "command": "python",
      "args": [
        "/absolute/path/to/stb-tester-main/mcp_server/stb_tester_server.py"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/stb-tester-main"
      }
    }
  }
}
```

### Claude Code

Add to your project's `.mcp.json` or global MCP configuration:

```json
{
  "servers": {
    "stb-tester": {
      "command": "python",
      "args": ["mcp_server/stb_tester_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Available Tools

### Remote Device Tools (Portal API)

These tools allow you to connect to real STB Tester nodes via the Portal API.

#### Setup for Remote Devices

Set environment variables:
```bash
export STBT_PORTAL_URL="https://your-company.stb-tester.com"
export STBT_PORTAL_TOKEN="your-api-token"
```

Or in `.mcp.json`:
```json
{
  "servers": {
    "stb-tester": {
      "command": "python",
      "args": ["mcp_server/stb_tester_server.py"],
      "env": {
        "STBT_PORTAL_URL": "https://your-company.stb-tester.com",
        "STBT_PORTAL_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### `stb_list_devices`
List all available STB Tester nodes.

```json
{}
```

Returns list of available devices with their status.

#### `stb_connect_device`
Connect to a specific STB Tester node.

```json
{
  "device_id": "stb-tester-node-001"
}
```

#### `stb_device_info`
Get detailed information about a device.

```json
{
  "device_id": "stb-tester-node-001"
}
```

#### `stb_device_screenshot`
Capture screenshot from a remote device. Returns the actual image for Claude to analyze.

```json
{
  "device_id": "stb-tester-node-001",
  "save_path": "/optional/path/to/save.png"
}
```

#### `stb_device_press`
Send a key press to a remote device.

```json
{
  "key": "KEY_HOME",
  "device_id": "stb-tester-node-001"
}
```

#### `stb_run_test`
Run a test script on a remote device.

```json
{
  "test_pack": "my-test-pack",
  "test_case": "tests/test_epg.py::test_open_guide",
  "device_id": "stb-tester-node-001"
}
```

#### `stb_job_status`
Get status of a running test job.

```json
{
  "job_id": "job-12345"
}
```

### Local Navigation & Control

#### `stb_press`
Press a remote control key.

```json
{
  "key": "KEY_OK"
}
```

Common keys: `KEY_UP`, `KEY_DOWN`, `KEY_LEFT`, `KEY_RIGHT`, `KEY_OK`, `KEY_BACK`, `KEY_HOME`, `KEY_EPG`, `KEY_PLAY`, `KEY_PAUSE`, `KEY_STOP`, `KEY_FASTFORWARD`, `KEY_REWIND`, `KEY_0` through `KEY_9`, `KEY_RED`, `KEY_GREEN`, `KEY_YELLOW`, `KEY_BLUE`

#### `stb_press_and_wait`
Press a key and wait for the screen to stabilize.

```json
{
  "key": "KEY_EPG",
  "stable_secs": 2
}
```

#### `stb_press_until_match`
Press a key repeatedly until a target image appears.

```json
{
  "key": "KEY_DOWN",
  "image": "reference_images/epg/bbc_one.png",
  "max_presses": 10,
  "interval_secs": 0.5
}
```

### Image Matching

#### `stb_match`
Check if a reference image is currently visible.

```json
{
  "image": "reference_images/common/logo.png",
  "region": {
    "x": 0,
    "y": 0,
    "width": 200,
    "height": 100
  }
}
```

#### `stb_wait_for_match`
Wait for an image to appear on screen.

```json
{
  "image": "reference_images/epg/guide.png",
  "timeout_secs": 10
}
```

### Motion Detection

#### `stb_wait_for_motion`
Wait for video motion (verifies playback).

```json
{
  "timeout_secs": 5,
  "region": {
    "x": 100,
    "y": 100,
    "width": 1720,
    "height": 880
  }
}
```

### Text Recognition

#### `stb_ocr`
Read text from the screen using OCR.

```json
{
  "region": {
    "x": 100,
    "y": 50,
    "width": 400,
    "height": 30
  },
  "mode": "SINGLE_LINE"
}
```

OCR modes: `PAGE`, `SINGLE_LINE`, `SINGLE_WORD`, `SINGLE_CHAR`

### Screenshots

#### `stb_screenshot`
Capture a screenshot from the current video frame.

```json
{
  "save_path": "/path/to/screenshot.png"
}
```

### Configuration

#### `stb_get_config`
Get STB Tester configuration values.

```json
{
  "section": "match",
  "key": "match_threshold"
}
```

### Menu Navigation

#### `stb_navigate_menu`
Navigate through menus to find a target item.

```json
{
  "target_text": "Settings",
  "direction": "down",
  "max_steps": 20,
  "text_region": {
    "x": 50,
    "y": 200,
    "width": 300,
    "height": 50
  }
}
```

Or with image matching:

```json
{
  "target_image": "reference_images/settings/settings_icon.png",
  "direction": "right",
  "max_steps": 5
}
```

## Example Usage

### From Claude Desktop or Claude Code

Once configured, you can ask Claude to interact with your set-top box:

> "Open the EPG guide and navigate to BBC One"

Claude will use the MCP tools to:
1. Press the EPG key
2. Wait for the guide to appear
3. Navigate down to find BBC One
4. Select the channel

### Programmatic Usage

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_stb():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server/stb_tester_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Press EPG key
            result = await session.call_tool("stb_press", {"key": "KEY_EPG"})
            print(result)

            # Wait for guide
            result = await session.call_tool("stb_wait_for_match", {
                "image": "reference_images/epg/guide.png",
                "timeout_secs": 5
            })
            print(result)

asyncio.run(test_stb())
```

## Interactive Device Usage

With a connected remote device, you can interact conversationally:

```
You: "Connect to device stb-node-001 and show me the home screen"

Claude:
1. Connects to device using stb_connect_device
2. Captures screenshot using stb_device_screenshot
3. Shows you the image and describes what's visible

You: "Navigate to Movies & Series and play something"

Claude:
1. Presses navigation keys using stb_device_press
2. Takes screenshots to verify navigation
3. Selects content and verifies playback

You: "Create a test script for what we just did"

Claude:
1. Generates a Python test script from the steps performed
2. Includes proper assertions for verification
```

### Example Conversation

```
User: List available devices

Claude: [Uses stb_list_devices]
Found 3 devices:
- stb-node-001 (idle)
- stb-node-002 (busy)
- stb-node-003 (idle)

User: Connect to stb-node-001 and show me what's on screen

Claude: [Uses stb_connect_device, then stb_device_screenshot]
Connected to stb-node-001. Here's the current screen:
[Shows screenshot]
I can see the home screen with options for Live TV, Movies, Settings...

User: Navigate to Movies and verify a movie is playing

Claude: [Uses stb_device_press KEY_RIGHT, KEY_OK, etc., with screenshots]
Done! I've navigated to Movies and selected the first item.
Motion detected - video is playing successfully.
```

## Mock Mode

If `stbt_core` is not available and Portal API is not configured, the server runs in mock mode. All tools return simulated successful responses. This is useful for:

- Development and testing without hardware
- CI/CD pipelines
- Learning the API

## Troubleshooting

### "MCP SDK not installed"

Install the MCP SDK:
```bash
pip install mcp
```

### "stbt_core not available"

The server will run in mock mode. For real device control, ensure STB Tester is installed and configured with your video capture device.

### Connection Issues

1. Check the server is running: `python mcp_server/stb_tester_server.py`
2. Verify the path in your MCP configuration is absolute
3. Ensure PYTHONPATH includes the stb-tester-main directory

## Development

Run tests:
```bash
pip install -e ".[dev]"
pytest
```

## License

MIT License - see the main STB Tester repository for details.
