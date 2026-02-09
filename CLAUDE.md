# STB Tester Test Script Generation

This project uses Claude Code to generate STB tester test scripts from high-level requirements.

## Default Device Configuration

**IMPORTANT:** Always use this device for building and running test cases:

| Setting | Value |
|---------|-------|
| **Device ID** | `stb-tester-48b02d5b0ab7` |
| **Friendly Name** | EOSv2_PROD |
| **Portal URL** | https://ziggo.stb-tester.com |
| **API Token** | cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs |

### API Endpoints

```bash
# Screenshot
curl -s 'https://ziggo.stb-tester.com/api/v2/nodes/stb-tester-48b02d5b0ab7/screenshot.png' \
  -H 'Authorization: token cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs' -o screenshot.png

# Press Key
curl -s -X POST 'https://ziggo.stb-tester.com/api/v2/nodes/stb-tester-48b02d5b0ab7/press' \
  -H 'Authorization: token cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs' \
  -H 'Content-Type: application/json' \
  -d '{"key": "KEY_MENU"}'

# Run Test
curl -s -X POST 'https://ziggo.stb-tester.com/api/v2/run_tests' \
  -H 'Authorization: token cBqdzRDwYbX1LI6cmskfsycAXNAIZPSs' \
  -H 'Content-Type: application/json' \
  -d '{"node_id": "stb-tester-48b02d5b0ab7", "test_pack_revision": "main", "test_cases": ["tests/example.py::test_name"]}'
```

---

## Test Case Registry

**IMPORTANT:** Before running any test case:
1. **Grounding:** Verify the test case name exists in this registry
2. **Check path:** Use the correct file path from the registry
3. **Run:** Execute via Portal API or `stbt run`

When creating new test cases:
1. Build and test the new test case
2. Commit to GitHub repository
3. **ADD the new test case to this registry below**

### Ziggo Test Pack (stb-tester-test-pack-ziggo/tests/)

| File | Test Function | Description |
|------|---------------|-------------|
| `eos_sanity.py` | `test_eos_sanity_5654` | EOS sanity check |
| `eos_sanity_SoftwareCheck.py` | `test_eos_sanity_softwareversion` | Software version verification |
| `live_tv_testcases.py` | `test_livetv_pause_and_playback_review_buffer` | Pause and review buffer |
| `live_tv_testcases.py` | `test_home_radio` | Home radio functionality |
| `live_tv_testcases.py` | `test_home_PIP_2215` | PIP functionality |
| `live_tv_testcases.py` | `test_live_tv_wrong_LCN` | Wrong LCN handling |
| `live_tv_testcases.py` | `test_teletext_availability` | Teletext availability |
| `live_tv_testcases.py` | `test_teletext_transperancy` | Teletext transparency |
| `live_tv_testcases.py` | `test_live_tv_record_an_episode` | Record episode |
| `live_tv_testcases.py` | `test_asset_detailed_page_logo` | Asset detail page logo |
| `live_tv_testcases.py` | `test_vod_purchase` | VOD purchase flow |
| `live_tv_testcases.py` | `test_VOD_providers` | VOD providers |
| `live_tv_testcases.py` | `test_create_delete_profile` | Profile management |
| `live_tv_testcases.py` | `test_personal_home_posters` | Personal home posters |
| `tv_guide_testcases.py` | `test_check_info_availability_guide` | Guide info availability |
| `tv_guide_testcases.py` | `test_PIP_check_guide` | PIP in guide |
| `tv_guide_testcases.py` | `test_seven_days_availability_guide` | 7-day guide availability |
| `tv_guide_testcases.py` | `test_fourteen_days_availability_guide` | 14-day guide availability |
| `tv_guide_testcases.py` | `test_forward_backward_check_guide` | Forward/backward navigation |
| `tv_guide_testcases.py` | `test_synopsis_guide` | Synopsis display |
| `tv_guide_testcases.py` | `test_sort_by_genre_guide` | Sort by genre |
| `tv_guide_testcases.py` | `test_replay_availability_guide` | Replay availability |
| `kids_section_testcases.py` | `test_kids_section_available` | Kids section availability |
| `kids_section_testcases.py` | `test_kids_section_enter_and_verify` | Enter kids section |
| `kids_section_testcases.py` | `test_kids_section_navigation_from_menu` | Kids navigation from menu |
| `kids_skyshowtime_exploration.py` | `test_kids_skyshowtime_exploration` | Kids SkyShowtime exploration |
| `tutorial.py` | `test_playback_from_guide` | Playback from guide |
| `tutorial.py` | `test_menu_navigation_apps` | Menu navigation to apps |
| `tutorial.py` | `test_menu_navigation_test` | Menu navigation test |
| `tutorial.py` | `test_find_program_for_rent` | Find program for rent |
| `tutorial.py` | `test_rent_and_playback` | Rent and playback flow |
| `tennis_australianopen_testcase.py` | `test_tennis_australianopen_jan31` | Australian Open Jan 31 |
| `tennis_australianopen_testcase.py` | `test_tennis_navigation_only` | Tennis navigation only |
| `wintersports_speedskating_testcase.py` | `test_wintersports_speedskating_jan24` | Speed skating Jan 24 |
| `wintersports_speedskating_testcase.py` | `test_wintersports_navigation_only` | Wintersports navigation |
| `csxxxx_error_monitoring_testcase.py` | `test_csxxxx_error_monitoring_4hours` | Error monitoring 4 hours |
| `csxxxx_error_monitoring_testcase.py` | `test_csxxxx_error_monitoring_2min_mock` | Error monitoring 2 min mock |
| `csxxxx_error_monitoring_testcase.py` | `test_csxxxx_error_monitoring_rtl4_only` | RTL4 error monitoring |
| `csxxxx_error_monitoring_testcase.py` | `test_csxxxx_error_monitoring_rtl5_only` | RTL5 error monitoring |
| `csxxxx_error_monitoring_testcase.py` | `test_error_detection_single_check` | Single error detection |
| `csxxxx_error_monitoring_testcase.py` | `test_channel_switch_recovery_validation` | Channel switch recovery |
| `csxxxx_error_monitoring_5min_validation.py` | `test_csxxxx_error_monitoring_5min_validation` | 5 min error validation |

### Local Test Pack (stb_tests/)

| File | Test Function | Description |
|------|---------------|-------------|
| `test_epg.py` | `test_open_epg_from_home` | Open EPG from home |
| `test_epg.py` | `test_open_epg_from_live_tv` | Open EPG from live TV |
| `test_epg.py` | `test_epg_shows_program_information` | EPG shows program info |
| `test_epg.py` | `test_epg_header_displayed` | EPG header displayed |
| `test_epg.py` | `test_navigate_channels_down` | Navigate channels down |
| `test_epg.py` | `test_navigate_channels_up` | Navigate channels up |
| `test_epg.py` | `test_navigate_time_slots_forward` | Navigate time forward |
| `test_epg.py` | `test_navigate_time_slots_backward` | Navigate time backward |
| `test_epg.py` | `test_fast_navigation_with_ff_rewind` | Fast navigation FF/RW |
| `test_epg.py` | `test_direct_channel_number_entry` | Direct channel entry |
| `test_epg.py` | `test_select_current_program` | Select current program |
| `test_epg.py` | `test_select_channel_and_verify_tuning` | Select and verify tuning |
| `test_epg.py` | `test_navigate_to_past_7_days` | Navigate to past 7 days |
| `test_epg.py` | `test_navigate_to_future_14_days` | Navigate to future 14 days |
| `test_epg.py` | `test_pip_available_in_epg` | PIP in EPG |
| `test_epg.py` | `test_program_synopsis_displayed` | Synopsis displayed |
| `test_epg.py` | `test_program_title_displayed` | Title displayed |
| `test_epg.py` | `test_close_epg_with_back_key` | Close EPG with BACK |
| `test_epg.py` | `test_close_epg_with_home_key` | Close EPG with HOME |
| `test_epg.py` | `test_replay_icon_displayed_for_past_programs` | Replay icon for past |
| `test_epg.py` | `test_start_replay_from_epg` | Start replay from EPG |
| `test_epg.py` | `test_epg_basic_functionality` | EPG basic functionality |
| `test_epg.py` | `test_epg_channel_surfing` | EPG channel surfing |
| `test_epg.py` | `test_epg_ocr_validation` | EPG OCR validation |
| `test_sports_football.py` | `test_navigate_to_sports_and_find_napoli_match` | Sports > Football > Napoli |
| `test_sports_football.py` | `test_sports_section_accessible` | Sports section accessible |
| `test_sports_football.py` | `test_direct_navigation_to_football` | Direct navigation to Football |
| `test_ziggo_menu_navigation.py` | `test_open_menu_from_live_tv` | Open menu from live TV |
| `test_ziggo_menu_navigation.py` | `test_navigate_to_entertainment` | Navigate to Entertainment |
| `test_ziggo_menu_navigation.py` | `test_select_and_play_content` | Select and play content |
| `test_ziggo_menu_navigation.py` | `test_full_journey_menu_to_playback` | Full menu to playback journey |
| `test_ziggo_menu_navigation.py` | `test_tune_to_channel_1` | Tune to channel 1 |
| `test_ziggo_menu_navigation.py` | `test_menu_opens` | Menu opens test |

---

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

---

## Test Execution Workflow

### Running a Test Case

When asked to run a test case, follow this workflow:

1. **Grounding (Verification)**
   - Search the Test Case Registry above for the requested test
   - Verify the exact test function name and file path
   - If test not found, inform user and suggest similar tests

2. **Execute Test**
   - Use device `stb-tester-48b02d5b0ab7`
   - Run via Portal API or manual key presses
   - Capture screenshots to verify results

3. **Report Results**
   - Show screenshots of key steps
   - Report pass/fail status
   - Document any errors encountered

### Creating a New Test Case

When asked to create a new test case:

1. **Build the Test**
   - Create test file in `stb_tests/` directory
   - Follow naming convention: `test_<feature>.py`
   - Include docstrings with Given/When/Then

2. **Test on Device**
   - Run the test on device `stb-tester-48b02d5b0ab7`
   - Verify it passes
   - Capture evidence screenshots

3. **Commit to GitHub**
   - Git add and commit the new test file
   - Push to remote repository

4. **UPDATE THIS REGISTRY**
   - **CRITICAL:** Add the new test case to the Test Case Registry section above
   - Include: File name, Test function, Description
   - This ensures the test is discoverable for future runs

### Example Test Run Request

```
User: "Run the Napoli match test"

Claude:
1. GROUNDING: Search registry for "napoli"
   → Found: test_sports_football.py::test_navigate_to_sports_and_find_napoli_match

2. EXECUTE: Run on device stb-tester-48b02d5b0ab7
   - Press MENU
   - Navigate to Sports
   - Navigate to Football
   - Search for Napoli

3. REPORT: Show screenshots and results
```

---
