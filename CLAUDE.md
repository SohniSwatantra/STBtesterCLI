# STB Tester Test Script Generation

This project uses Claude Code to generate STB tester test scripts from high-level requirements.

## Workflows

### Workflow 1: Text-Based Specification
1. **Define test specifications** in `TEST_SPECS.md` using Given/When/Then format
2. **Ask Claude Code** to generate test scripts from the specifications
3. **Review and refine** the generated tests
4. **Add reference images** as needed to `reference_images/`

### Workflow 2: Video/Screenshot-Based Generation (Recommended)

Claude can analyze videos or screenshots to automatically generate test scripts!

#### How It Works

1. **Provide a video or screenshots** showing the user journey you want to test
2. **Describe your acceptance criteria** (e.g., "verify movie is playing")
3. **Claude analyzes the visuals** and extracts:
   - Navigation steps (which keys to press)
   - UI elements to verify (for image matching)
   - Text to check (for OCR)
   - Expected states (motion for playback)
4. **Claude generates the complete test script**

#### Example Usage

```
User: [Attaches video showing: Home → Movies & Series → Select Movie → Playback]

"Generate a test that navigates to Movies & Series from home,
selects the first movie, and verifies it starts playing.

Acceptance Criteria:
- Movies & Series section is reached
- A movie is selected
- Video playback starts (motion detected)"
```

Claude will:
1. Watch the video to understand the UI flow
2. Identify key frames for reference images
3. Extract navigation sequence (KEY_RIGHT, KEY_DOWN, KEY_OK, etc.)
4. Generate test script with proper assertions

#### Tips for Video-Based Generation

- **Show the complete flow** from start to end state
- **Include failure states** if you want error handling
- **Pause on important screens** so Claude can identify UI elements
- **Describe edge cases** in your acceptance criteria
- **Provide device context** (device type, resolution, remote layout)

### Workflow 3: Live Device Interaction via MCP

With a connected STB Tester node, Claude can:
1. **Connect to your real device** by device ID
2. **Explore the UI interactively** - taking screenshots, pressing keys
3. **Build test scripts** based on live exploration
4. **Run and verify tests** in real-time

See "MCP Server - Real Device Connection" section below.

## How to Generate Tests

When asked to generate a test, read the specification from `TEST_SPECS.md` and create a pytest-compatible test file in `tests/`.

### Naming Conventions

- Test directory: `stb_tests/` (separate from library's own `tests/` directory)
- Test files: `test_<feature>.py` (e.g., `test_epg_navigation.py`)
- Test functions: `test_<scenario_name>` (e.g., `test_navigate_to_bbc_one`)
- Reference images: `<feature>/<descriptive_name>.png` (e.g., `epg/guide_open.png`)

## STB Tester API Reference

### Key Press Operations

```python
import stbt_core as stbt

# Single key press
stbt.press("KEY_EPG")

# Press and wait for screen to stabilize
stbt.press_and_wait("KEY_OK", stable_secs=1)

# Press until a target appears
stbt.press_until_match("KEY_DOWN", "reference_images/target.png", max_presses=10)
```

### Image Matching

```python
# Wait for an image to appear
stbt.wait_for_match("reference_images/epg/guide.png", timeout_secs=10)

# Check if image is present (returns MatchResult)
result = stbt.match("reference_images/logo.png")
assert result.match  # True if found

# Match in specific region
region = stbt.Region(x=0, y=0, width=200, height=100)
result = stbt.match("reference_images/logo.png", region=region)
```

### Motion Detection

```python
# Wait for video motion (confirms playback)
stbt.wait_for_motion(timeout_secs=5)

# Detect motion in specific region
stbt.wait_for_motion(timeout_secs=5, region=stbt.Region(x=100, y=100, width=500, height=400))
```

### OCR (Text Recognition)

```python
# Read text from screen region
text = stbt.ocr(region=stbt.Region(x=100, y=100, width=300, height=50))
assert "BBC One" in text

# OCR with mode
text = stbt.ocr(mode=stbt.OcrMode.PAGE)
```

### Wait Conditions

```python
from stbt_core import wait_until

# Wait for a condition
assert wait_until(lambda: stbt.match("reference_images/ready.png"))

# Wait with timeout
assert wait_until(lambda: stbt.match("reference_images/ready.png"), timeout_secs=10)
```

### Regions

```python
# Define screen regions for targeted operations
header_region = stbt.Region(x=0, y=0, width=1920, height=100)
content_region = stbt.Region(x=200, y=150, width=1520, height=800)
```

## Test Structure Template

```python
import pytest
import stbt_core as stbt

class TestFeatureName:
    """Tests for <Feature Name>."""

    def setup_method(self):
        """Reset to known state before each test."""
        # Navigate to home or known starting point
        pass

    def test_scenario_name(self):
        """
        Scenario: <Scenario description>

        Given: <precondition>
        When: <action>
        Then: <expected result>
        """
        # Given: Setup preconditions

        # When: Perform actions

        # Then: Assert expected results
        pass
```

## Common Patterns

### Navigate to Home Screen
```python
def navigate_to_home():
    stbt.press("KEY_HOME")
    stbt.wait_for_match("reference_images/home_screen.png", timeout_secs=5)
```

### Open EPG Guide
```python
def open_epg():
    stbt.press("KEY_EPG")
    stbt.wait_for_match("reference_images/epg/guide.png", timeout_secs=5)
```

### Select Channel by Name (using OCR)
```python
def select_channel(channel_name, max_attempts=20):
    for _ in range(max_attempts):
        text = stbt.ocr(region=channel_list_region)
        if channel_name in text:
            stbt.press("KEY_OK")
            return True
        stbt.press("KEY_DOWN")
    raise Exception(f"Channel {channel_name} not found")
```

### Verify Video Playback
```python
def verify_video_playing():
    stbt.wait_for_motion(timeout_secs=5)
```

## Reference Images

Store reference images in `reference_images/` with subdirectories:

```
reference_images/
├── epg/           # EPG guide screenshots
├── playback/      # Playback UI elements
├── settings/      # Settings screens
└── common/        # Shared elements (logos, buttons)
```

## Test Categories

When generating tests, organize them in `stb_tests/` by category:

- `stb_tests/test_epg_*.py` - EPG/Guide navigation tests
- `stb_tests/test_playback_*.py` - Video playback tests
- `stb_tests/test_settings_*.py` - Settings/configuration tests
- `stb_tests/test_channel_*.py` - Channel tuning tests

## Best Practices

1. **Use descriptive test names** that explain the scenario
2. **Add docstrings** with Given/When/Then for traceability
3. **Use fixtures** from `conftest.py` for common setup
4. **Handle timeouts gracefully** - use appropriate timeout values
5. **Use regions** to limit image matching/OCR scope for reliability
6. **Verify state** before and after critical actions

## MCP Server

This project includes an MCP (Model Context Protocol) server that exposes STB Tester APIs as tools. This allows Claude to directly control set-top boxes during conversations.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `stb_press` | Press a remote control key |
| `stb_press_and_wait` | Press key and wait for screen stability |
| `stb_press_until_match` | Press key repeatedly until image found |
| `stb_match` | Check if image is visible on screen |
| `stb_wait_for_match` | Wait for image to appear |
| `stb_wait_for_motion` | Verify video playback |
| `stb_ocr` | Read text from screen |
| `stb_screenshot` | Capture current frame |
| `stb_navigate_menu` | Navigate menus to find target |

### Configuration

The project includes `.mcp.json` for Claude Code integration. See `mcp_server/README.md` for detailed setup instructions.

### Example MCP Usage

Ask Claude to:
- "Press the EPG key and wait for the guide to appear"
- "Navigate down until you find BBC One"
- "Check if video is playing"
- "Read the channel name from the screen"

### Real Device Connection

The MCP server supports connecting to real STB Tester nodes via the Portal API.

#### Setup

1. Get your STB Tester Portal API token from https://portal.stb-tester.com
2. Configure the MCP server with your credentials:

```bash
export STBT_PORTAL_URL="https://your-company.stb-tester.com"
export STBT_PORTAL_TOKEN="your-api-token"
```

Or add to `.mcp.json`:
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

#### Device Connection Tools

| Tool | Description |
|------|-------------|
| `stb_list_devices` | List available STB Tester nodes |
| `stb_connect_device` | Connect to a specific device by ID |
| `stb_device_screenshot` | Capture screenshot from connected device |
| `stb_device_press` | Send key press to connected device |
| `stb_run_test` | Run a test script on the device |

#### Example: Live Device Interaction

```
User: "Connect to device stb-node-001 and show me what's on screen"

Claude:
1. Uses stb_connect_device(device_id="stb-node-001")
2. Uses stb_device_screenshot() to capture current frame
3. Shows the screenshot and describes what's visible

User: "Navigate to Settings and take a screenshot"

Claude:
1. Uses stb_device_press(key="KEY_HOME")
2. Uses stb_device_press(key="KEY_RIGHT") to navigate
3. Uses stb_device_screenshot() to show result
```

#### Interactive Test Development

With a connected device, you can develop tests interactively:

1. **Explore**: "Show me the home screen"
2. **Navigate**: "Press RIGHT three times and show me"
3. **Verify**: "What text is visible in the header?"
4. **Generate**: "Create a test script for what we just did"
