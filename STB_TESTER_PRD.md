# STB Tester Automated Test Suite - Product Requirements Document

## Overview
Build a comprehensive automated test suite for Set-Top Box (STB) testing using the STB Tester framework. The test suite will cover EPG navigation, video playback, settings configuration, and Ziggo-specific menu navigation scenarios.

## Project Goals
1. Generate pytest-compatible test scripts from user story specifications
2. Implement reliable STB testing using stbt_core library
3. Support both local and remote device testing via MCP integration
4. Create reusable test patterns and helper functions

## Technical Stack
- **Testing Framework**: pytest with stbt_core
- **STB Library**: stbt_core (press, wait_for_match, wait_for_motion, ocr)
- **Remote Control**: MCP server for Claude Code integration
- **Image Matching**: OpenCV-based reference image comparison
- **OCR**: Tesseract-based text recognition

---

## User Stories & Test Cases

### Epic 1: EPG/Guide Navigation Tests

#### US-001: Open EPG Guide
**As a** viewer
**I want to** open the Electronic Program Guide
**So that** I can see what's on TV

**Acceptance Criteria:**
- EPG opens when pressing the EPG/Guide key
- EPG displays channel list
- Current channel is highlighted

**Scenarios:**
1. Open EPG from Live TV
   - Given: Device is playing live TV
   - When: User presses the EPG key
   - Then: EPG guide overlay appears, current time slot is visible, channel list is displayed

---

#### US-002: Navigate EPG Channel List
**As a** viewer
**I want to** navigate through channels in the EPG
**So that** I can find programs to watch

**Acceptance Criteria:**
- Can scroll up/down through channel list
- Channel information updates as selection moves
- Can select a channel to tune

**Scenarios:**
1. Scroll Down Channel List
   - Given: EPG guide is open
   - When: User presses DOWN key multiple times
   - Then: Selection moves to next channel, channel info panel updates

2. Select Channel from EPG
   - Given: EPG guide is open and a channel is highlighted
   - When: User presses OK/Select
   - Then: EPG closes, selected channel tunes, video starts playing

---

#### US-003: Tune to BBC One from EPG
**As a** viewer
**I want to** access BBC One from the EPG guide
**So that** I can watch my favorite shows

**Acceptance Criteria:**
- EPG guide opens when pressing EPG key
- Can navigate to BBC One
- Channel tunes successfully with video playing

**Scenarios:**
1. Basic EPG Navigation to BBC One
   - Given: Device is on any channel
   - When: User presses EPG key and navigates to BBC One
   - Then: EPG Guide appears, BBC One channel is found and selected, video is playing

---

### Epic 2: Video Playback Tests

#### US-004: Pause and Resume Live TV
**As a** viewer
**I want to** pause live TV
**So that** I can take a break without missing content

**Acceptance Criteria:**
- Pause icon appears when paused
- Video freezes (no motion)
- Resume continues from paused point
- Video motion resumes on play

**Scenarios:**
1. Pause Live TV
   - Given: Live TV is playing with visible motion
   - When: User presses PAUSE
   - Then: Pause indicator appears, video motion stops

2. Resume from Pause
   - Given: Live TV is paused
   - When: User presses PLAY
   - Then: Pause indicator disappears, video motion resumes

---

#### US-005: Fast Forward and Rewind
**As a** viewer
**I want to** fast forward and rewind recorded content
**So that** I can skip or replay sections

**Acceptance Criteria:**
- Fast forward increases playback speed
- Rewind plays content backwards
- Speed indicator shows current mode

**Scenarios:**
1. Fast Forward at 2x Speed
   - Given: Recorded content is playing
   - When: User presses FAST_FORWARD once
   - Then: Speed indicator shows 2x, content advances faster

2. Rewind Content
   - Given: Recorded content is playing
   - When: User presses REWIND
   - Then: Rewind indicator appears, content plays in reverse

---

#### US-006: VOD Content Playback
**As a** viewer
**I want to** play Video on Demand content
**So that** I can watch movies and shows anytime

**Acceptance Criteria:**
- VOD content starts playing when selected
- Playback controls work (play/pause/seek)
- Progress bar shows current position

**Scenarios:**
1. Start VOD Playback
   - Given: User has selected a VOD title
   - When: User presses PLAY/OK
   - Then: Video starts playing, motion is detected, progress bar appears

---

### Epic 3: Settings & Configuration Tests

#### US-007: Access Settings Menu
**As a** user
**I want to** access the settings menu
**So that** I can configure my device preferences

**Acceptance Criteria:**
- Settings menu opens from home screen
- All setting categories are visible
- Can navigate between settings

**Scenarios:**
1. Open Settings from Home
   - Given: Device is on home screen
   - When: User navigates to Settings and presses OK
   - Then: Settings menu appears, setting categories are displayed

---

#### US-008: Change Audio Settings
**As a** user
**I want to** change audio settings
**So that** I can optimize sound for my setup

**Acceptance Criteria:**
- Audio settings section is accessible
- Volume/audio options are available
- Changes are applied and saved

**Scenarios:**
1. Navigate to Audio Settings
   - Given: Settings menu is open
   - When: User navigates to Audio section
   - Then: Audio settings are displayed, options can be modified

---

#### US-009: Network Settings
**As a** user
**I want to** configure network settings
**So that** my device stays connected

**Acceptance Criteria:**
- Network settings show connection status
- WiFi networks can be viewed
- Connection status is accurate

**Scenarios:**
1. View Network Status
   - Given: Settings menu is open
   - When: User navigates to Network settings
   - Then: Current connection status is displayed, network type shown

---

### Epic 4: Ziggo Menu Navigation Tests

#### US-010: Navigate from Live TV to Ziggo Menu
**As a** Ziggo viewer
**I want to** access the main menu from live TV
**So that** I can browse Movies & Series content

**Acceptance Criteria:**
- Menu opens when pressing MENU key from live TV
- Menu displays categories: For You, Apps, Entertainment, Sports, Recordings
- Content is visible and selectable
- Selected content plays with video motion

**Scenarios:**
1. Open Menu from Live TV
   - Given: Device is playing live TV (e.g., Ziggo Sport)
   - When: User presses MENU key
   - Then: Main menu overlay appears, "For You" section displayed, menu categories visible

2. Navigate to Entertainment
   - Given: Main menu is open on "For You" tab
   - When: User navigates RIGHT to Entertainment section
   - Then: Entertainment category becomes selected, Entertainment content displayed

3. Select and Play Content
   - Given: User is viewing content in the menu
   - When: User navigates to "Watch" button and presses OK
   - Then: Content begins loading, video playback starts, motion detected

**Key Sequence:**
```
KEY_BACK (x4)  → Exit any overlays, return to live TV
KEY_1          → Tune to channel 1 (optional)
KEY_MENU       → Open Ziggo main menu
KEY_DOWN       → Navigate to content
KEY_OK         → Select content / Watch
```

**Reference Images:**
- `reference_images/ziggo/live_tv_sports.jpg` - Live TV state
- `reference_images/ziggo/menu_for_you.jpg` - Menu with "For You" section

---

## Technical Requirements

### Test Structure
```python
# Each test file follows this pattern:
import pytest
import stbt_core as stbt

class TestFeatureName:
    def setup_method(self):
        """Reset to known state"""
        pass

    def test_scenario_name(self):
        """Given/When/Then docstring"""
        # Given: preconditions
        # When: actions
        # Then: assertions
```

### Common Patterns
- `stbt.press("KEY_*")` - Press remote control key
- `stbt.wait_for_match("image.png", timeout_secs=10)` - Wait for image
- `stbt.wait_for_motion(timeout_secs=5)` - Verify video playing
- `stbt.ocr(region=stbt.Region(...))` - Read text from screen

### Directory Structure
```
stb_tests/
├── conftest.py              # Shared fixtures
├── test_epg_navigation.py   # EPG tests (US-001, US-002, US-003)
├── test_playback.py         # Playback tests (US-004, US-005, US-006)
├── test_settings.py         # Settings tests (US-007, US-008, US-009)
└── test_ziggo_menu.py       # Ziggo tests (US-010)

reference_images/
├── epg/                     # EPG reference images
├── playback/                # Playback UI images
├── settings/                # Settings screens
└── ziggo/                   # Ziggo-specific images
```

---

## Priority & Phases

### Phase 1: Core Infrastructure (Priority: HIGH)
- [ ] Set up test directory structure
- [ ] Create conftest.py with common fixtures
- [ ] Implement helper functions for navigation

### Phase 2: EPG Tests (Priority: HIGH)
- [ ] US-001: Open EPG Guide test
- [ ] US-002: Navigate EPG Channel List tests
- [ ] US-003: Tune to BBC One test

### Phase 3: Playback Tests (Priority: MEDIUM)
- [ ] US-004: Pause and Resume tests
- [ ] US-005: Fast Forward and Rewind tests
- [ ] US-006: VOD Playback test

### Phase 4: Settings Tests (Priority: MEDIUM)
- [ ] US-007: Access Settings Menu test
- [ ] US-008: Audio Settings test
- [ ] US-009: Network Settings test

### Phase 5: Ziggo Integration (Priority: HIGH)
- [ ] US-010: Ziggo Menu Navigation tests
- [ ] Integration with MCP for remote device control

---

## Success Criteria
- All test scripts are pytest-compatible and can be run with `pytest stb_tests/`
- Tests use proper stbt_core APIs for image matching and motion detection
- Reference images are organized in appropriate directories
- Tests include proper error handling and timeouts
- Documentation includes examples of running tests

---

## Deliverables
1. `stb_tests/conftest.py` - Common fixtures and helpers
2. `stb_tests/test_epg_navigation.py` - EPG test suite
3. `stb_tests/test_playback.py` - Playback test suite
4. `stb_tests/test_settings.py` - Settings test suite
5. `stb_tests/test_ziggo_menu.py` - Ziggo menu test suite
6. Reference images in `reference_images/` directories
7. Updated TEST_SPECS.md with test mapping
