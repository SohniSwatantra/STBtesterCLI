# Test Specifications

This file contains test specifications written in **Specification by Example** format.
Claude Code reads these specifications to generate STB tester test scripts.

---

## How to Write Test Specifications

Each test case should include:

1. **Test Case Name** - Clear, descriptive title
2. **User Story** - Business context (As a... I want... So that...)
3. **Acceptance Criteria** - High-level requirements
4. **Scenarios** - Specific test scenarios with Given/When/Then

### Example Format

```markdown
## Test Case: [Descriptive Name]

### User Story
As a [user type], I want to [action] so that [benefit].

### Acceptance Criteria
- Criterion 1
- Criterion 2
- Criterion 3

### Scenarios

#### Scenario 1: [Scenario Name]
Given: [precondition/starting state]
When: [action performed]
Then:
- [expected outcome 1]
- [expected outcome 2]
```

---

# EPG/Guide Navigation Tests

## Test Case: Open EPG Guide

### User Story
As a viewer, I want to open the Electronic Program Guide so that I can see what's on TV.

### Acceptance Criteria
- EPG opens when pressing the EPG/Guide key
- EPG displays channel list
- Current channel is highlighted

### Scenarios

#### Scenario 1: Open EPG from Live TV
Given: Device is playing live TV
When: User presses the EPG key
Then:
- EPG guide overlay appears
- Current time slot is visible
- Channel list is displayed

---

## Test Case: Navigate EPG Channel List

### User Story
As a viewer, I want to navigate through channels in the EPG so that I can find programs to watch.

### Acceptance Criteria
- Can scroll up/down through channel list
- Channel information updates as selection moves
- Can select a channel to tune

### Scenarios

#### Scenario 1: Scroll Down Channel List
Given: EPG guide is open
When: User presses DOWN key multiple times
Then:
- Selection moves to next channel
- Channel info panel updates
- Scrolling continues smoothly

#### Scenario 2: Select Channel from EPG
Given: EPG guide is open and a channel is highlighted
When: User presses OK/Select
Then:
- EPG closes
- Selected channel tunes
- Video starts playing

---

## Test Case: Tune to BBC One from EPG Guide

### User Story
As a viewer, I want to access BBC One from the EPG guide so that I can watch my favorite shows.

### Acceptance Criteria
- EPG guide opens when pressing EPG key
- Can navigate to BBC One
- Channel tunes successfully with video playing

### Scenarios

#### Scenario 1: Basic EPG Navigation to BBC One
Given: Device is on any channel
When: User presses EPG key and navigates to BBC One
Then:
- EPG Guide appears
- BBC One channel is found and selected
- Video is playing (motion detected)

---

# Video Playback Tests

## Test Case: Pause and Resume Live TV

### User Story
As a viewer, I want to pause live TV so that I can take a break without missing content.

### Acceptance Criteria
- Pause icon appears when paused
- Video freezes (no motion)
- Resume continues from paused point
- Video motion resumes on play

### Scenarios

#### Scenario 1: Pause Live TV
Given: Live TV is playing with visible motion
When: User presses PAUSE
Then:
- Pause indicator appears on screen
- Video motion stops
- Timecode shows paused state

#### Scenario 2: Resume from Pause
Given: Live TV is paused
When: User presses PLAY
Then:
- Pause indicator disappears
- Video motion resumes
- Content continues from pause point

---

## Test Case: Fast Forward and Rewind

### User Story
As a viewer, I want to fast forward and rewind recorded content so that I can skip or replay sections.

### Acceptance Criteria
- Fast forward increases playback speed
- Rewind plays content backwards
- Speed indicator shows current mode
- Normal playback resumes on PLAY

### Scenarios

#### Scenario 1: Fast Forward at 2x Speed
Given: Recorded content is playing
When: User presses FAST_FORWARD once
Then:
- Speed indicator shows 2x
- Content advances faster than normal

#### Scenario 2: Rewind Content
Given: Recorded content is playing
When: User presses REWIND
Then:
- Rewind indicator appears
- Content plays in reverse

---

## Test Case: VOD Content Playback

### User Story
As a viewer, I want to play Video on Demand content so that I can watch movies and shows anytime.

### Acceptance Criteria
- VOD content starts playing when selected
- Playback controls work (play/pause/seek)
- Progress bar shows current position

### Scenarios

#### Scenario 1: Start VOD Playback
Given: User has selected a VOD title
When: User presses PLAY/OK
Then:
- Video starts playing
- Motion is detected
- Progress bar appears briefly

---

# Settings & Configuration Tests

## Test Case: Access Settings Menu

### User Story
As a user, I want to access the settings menu so that I can configure my device preferences.

### Acceptance Criteria
- Settings menu opens from home screen
- All setting categories are visible
- Can navigate between settings

### Scenarios

#### Scenario 1: Open Settings from Home
Given: Device is on home screen
When: User navigates to Settings and presses OK
Then:
- Settings menu appears
- Setting categories are displayed
- First category is highlighted

---

## Test Case: Change Audio Settings

### User Story
As a user, I want to change audio settings so that I can optimize sound for my setup.

### Acceptance Criteria
- Audio settings section is accessible
- Volume/audio options are available
- Changes are applied and saved

### Scenarios

#### Scenario 1: Navigate to Audio Settings
Given: Settings menu is open
When: User navigates to Audio section
Then:
- Audio settings are displayed
- Current settings are shown
- Options can be modified

---

## Test Case: Network Settings

### User Story
As a user, I want to configure network settings so that my device stays connected.

### Acceptance Criteria
- Network settings show connection status
- WiFi networks can be viewed
- Connection status is accurate

### Scenarios

#### Scenario 1: View Network Status
Given: Settings menu is open
When: User navigates to Network settings
Then:
- Current connection status is displayed
- Network type (WiFi/Ethernet) is shown
- Signal strength is indicated (if WiFi)

---

# Add Your Test Specifications Below

<!--
Add new test specifications following the format above.
Organize by category: EPG, Playback, Settings, etc.
-->

---

# Ziggo Menu Navigation Tests

*Generated from video analysis: video (8).mp4*
*Target Device: stb-tester-48b02d5b0ab7*

## Test Case: Navigate from Live TV to Ziggo Menu

### User Story
As a Ziggo viewer, I want to access the main menu from live TV so that I can browse Movies & Series content.

### Acceptance Criteria
- Menu opens when pressing MENU key from live TV
- Menu displays categories: For You, Apps, Entertainment, Sports, Recordings
- Content is visible and selectable
- Selected content plays with video motion

### Scenarios

#### Scenario 1: Open Menu from Live TV
Given: Device is playing live TV (e.g., Ziggo Sport)
When: User presses MENU key
Then:
- Main menu overlay appears
- "For You" section is displayed
- Menu categories are visible in header
- Featured content (e.g., Father Brown) is shown

#### Scenario 2: Navigate to Entertainment
Given: Main menu is open on "For You" tab
When: User navigates RIGHT to Entertainment section
Then:
- Entertainment category becomes selected
- Entertainment content is displayed

#### Scenario 3: Select and Play Content
Given: User is viewing content in the menu (e.g., Father Brown)
When: User navigates to "Watch" button and presses OK
Then:
- Content begins loading
- Video playback starts
- Motion is detected (video is playing)

### Key Sequence (from video)
```
KEY_BACK (x4)  → Exit any overlays, return to live TV
KEY_1          → Tune to channel 1 (optional)
KEY_MENU       → Open Ziggo main menu
KEY_DOWN       → Navigate to content
KEY_OK         → Select content / Watch
```

### Reference Images
- `reference_images/ziggo/live_tv_sports.jpg` - Live TV state
- `reference_images/ziggo/menu_for_you.jpg` - Menu with "For You" section

### Test Script
Generated: `stb_tests/test_ziggo_menu_navigation.py`

