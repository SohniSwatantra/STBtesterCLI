# STB Tester MCP Usage Guide

## Overview

The STB Tester MCP (Model Context Protocol) server allows Claude to directly interact with your STB Tester devices. Once configured, you can control devices, run tests, capture screenshots, and analyze results through natural conversation.

---

## Available MCP Tools

### 1. Device Management Tools

| Tool | Description | Example Prompt |
|------|-------------|----------------|
| `stb_list_devices` | List all STB Tester nodes | "List available devices" |
| `stb_connect_device` | Connect to a specific device | "Connect to stb-tester-48b02d5b0ab7" |
| `stb_device_info` | Get device details | "Show me device info" |

### 2. Remote Control Tools

| Tool | Description | Example Prompt |
|------|-------------|----------------|
| `stb_device_press` | Send key press to device | "Press the MENU key" |
| `stb_device_screenshot` | Capture screenshot | "Take a screenshot" |

### 3. Test Execution Tools

| Tool | Description | Example Prompt |
|------|-------------|----------------|
| `stb_run_test` | Run a test on device | "Run test_home_PIP_2215" |
| `stb_job_status` | Check test job status | "Check status of job 1184" |

### 4. Local STB Tester Tools (when running on STB hardware)

| Tool | Description |
|------|-------------|
| `stb_press` | Press remote key |
| `stb_press_and_wait` | Press and wait for stability |
| `stb_press_until_match` | Press until image appears |
| `stb_match` | Check if image is visible |
| `stb_wait_for_match` | Wait for image to appear |
| `stb_wait_for_motion` | Detect video playback |
| `stb_ocr` | Read text from screen |
| `stb_screenshot` | Capture frame |
| `stb_navigate_menu` | Navigate to target |

---

## Workflows

### Workflow 1: Interactive Device Exploration

**Goal**: Explore device UI, understand navigation, discover elements

**Example Conversation**:
```
You: "Connect to my Ziggo device and show me what's on screen"
Claude: [Connects, takes screenshot, describes what's visible]

You: "Press MENU and show me the options"
Claude: [Presses MENU, takes screenshot, lists menu items]

You: "Navigate to Entertainment section"
Claude: [Presses RIGHT keys, shows progress, confirms arrival]
```

### Workflow 2: Test Development from Video

**Goal**: Generate test scripts from recorded user journeys

**Example Conversation**:
```
You: "I've added a video showing navigation to Movies. Generate a test."
Claude: [Analyzes video frames, extracts steps, generates test script]

You: "Run that test on the device"
Claude: [Executes test, shows results, provides video link]
```

### Workflow 3: Automated Test Execution

**Goal**: Run existing tests and analyze results

**Example Conversation**:
```
You: "Run the PIP test on EOSv2_PROD"
Claude: [Executes test, monitors progress, reports pass/fail]

You: "Show me the video of that test"
Claude: [Provides video link and thumbnail]
```

### Workflow 4: Test History Analysis

**Goal**: Review past test results and identify issues

**Example Conversation**:
```
You: "Show me test history for the past month"
Claude: [Queries API, shows pass/fail rates, identifies flaky tests]

You: "What's causing test_launch_youtube to fail?"
Claude: [Analyzes failure reasons, suggests fixes]
```

### Workflow 5: Live Debugging

**Goal**: Debug issues interactively on real device

**Example Conversation**:
```
You: "The EPG isn't opening. Help me debug."
Claude: [Takes screenshot, checks current state]
Claude: "I see the device is on live TV. Let me try pressing EPG..."
Claude: [Presses EPG, takes screenshot, analyzes result]
```

---

## How to Prompt the MCP

### Basic Commands

| What You Want | How to Ask |
|---------------|------------|
| See current screen | "Take a screenshot" / "Show me the screen" |
| Press a key | "Press MENU" / "Press the OK button" |
| Navigate | "Go to Settings" / "Navigate to Entertainment" |
| Run test | "Run test_home_PIP_2215" / "Execute the PIP test" |
| Check results | "Show test history" / "What were the last test results?" |

### Key Names

Use these key names when asking to press buttons:
- Navigation: `KEY_UP`, `KEY_DOWN`, `KEY_LEFT`, `KEY_RIGHT`, `KEY_OK`, `KEY_BACK`
- Menu: `KEY_MENU`, `KEY_EPG`, `KEY_INFO`
- Playback: `KEY_PLAY`, `KEY_PAUSE`, `KEY_STOP`, `KEY_FASTFORWARD`, `KEY_REWIND`
- Numbers: `KEY_0` through `KEY_9`
- Colors: `KEY_RED`, `KEY_GREEN`, `KEY_YELLOW`, `KEY_BLUE`

### Natural Language Examples

You can use natural language - Claude will translate to the right tool:

```
"Show me what's on the Ziggo box"
-> Claude uses stb_device_screenshot

"Press right three times"
-> Claude uses stb_device_press (KEY_RIGHT) x 3

"Check if video is playing"
-> Claude uses stb_wait_for_motion

"Read the channel name"
-> Claude uses stb_ocr on appropriate region

"Find and select BBC One in the guide"
-> Claude uses stb_navigate_menu with OCR
```

---

## Configuration

### Setup in `.mcp.json`

```json
{
  "servers": {
    "stb-tester": {
      "command": "python",
      "args": ["mcp_server/stb_tester_server.py"],
      "env": {
        "PYTHONPATH": ".",
        "STBT_PORTAL_URL": "https://ziggo.stb-tester.com",
        "STBT_PORTAL_TOKEN": "your-api-token",
        "STBT_DEFAULT_DEVICE": "stb-tester-48b02d5b0ab7"
      }
    }
  }
}
```

### Your Current Configuration

- **Portal URL**: https://ziggo.stb-tester.com
- **Default Device**: stb-tester-48b02d5b0ab7 (EOSv2_PROD)
- **Backup Device**: stb-tester-48b02d5b18d4 (EOSv1_PROD)

---

## Example Session

Here's a complete example workflow:

```
You: "Connect to my device and open the main menu"

Claude: I'll connect to your device and open the menu.
[Uses stb_connect_device -> stb_device_screenshot -> stb_device_press(KEY_MENU) -> stb_device_screenshot]

Connected to EOSv2_PROD. Here's the menu:
[Shows screenshot]
I can see: For you | TV & Replay | Apps | Entertainment | Sports | Recordings

You: "Navigate to Entertainment and show me what's there"

Claude: [Uses stb_device_press(KEY_RIGHT) x 3 -> stb_device_press(KEY_OK) -> stb_device_screenshot]

Here's the Entertainment section:
[Shows screenshot]
I see movies and series including...

You: "Create a test script for this navigation"

Claude: Based on what we did, here's the test script:
[Generates Python test code with proper assertions]

You: "Run that test and give me the video"

Claude: [Uses stb_run_test -> monitors job -> retrieves video]

Test passed! Here's the video link: [URL]
```

---

## Files Created for MCP

| File | Location | Purpose |
|------|----------|---------|
| MCP Server | `mcp_server/stb_tester_server.py` | Main server code |
| Config | `.mcp.json` | Claude Code configuration |
| Documentation | `mcp_server/README.md` | Detailed API docs |
| Usage Guide | `MCP_USAGE_GUIDE.md` | This file - workflows and prompting guide |

---

## Verification

To verify MCP is working:
1. Ask Claude: "List available STB Tester devices"
2. If configured correctly, you'll see device list
3. Ask: "Take a screenshot from EOSv2_PROD"
4. You should see the current device screen

---

## Troubleshooting

### "Portal API not configured"

Ensure your `.mcp.json` has valid credentials:
```json
{
  "env": {
    "STBT_PORTAL_URL": "https://your-company.stb-tester.com",
    "STBT_PORTAL_TOKEN": "your-actual-token"
  }
}
```

### "No device connected"

Connect to a device first:
```
"Connect to stb-tester-48b02d5b0ab7"
```

### Screenshots not showing

Make sure the MCP server is running and the device is accessible via the Portal API.

### Test execution fails

1. Verify the test pack name is correct
2. Ensure the test case path matches your test structure
3. Check the device is idle and available

---

## Quick Reference Card

| Action | Prompt | Tool Used |
|--------|--------|-----------|
| List devices | "List devices" | `stb_list_devices` |
| Connect | "Connect to [device-id]" | `stb_connect_device` |
| Screenshot | "Take a screenshot" | `stb_device_screenshot` |
| Press key | "Press [KEY_NAME]" | `stb_device_press` |
| Run test | "Run [test_name]" | `stb_run_test` |
| Check job | "Status of job [id]" | `stb_job_status` |
| Detect playback | "Is video playing?" | `stb_wait_for_motion` |
| Read text | "Read the text on screen" | `stb_ocr` |
