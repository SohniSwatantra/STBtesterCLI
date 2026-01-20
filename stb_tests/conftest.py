"""
Shared pytest fixtures and helpers for STB Tester tests.

This module provides common fixtures, helper functions, and configuration
for all test modules in the stb_tests/ directory.
"""

import os
import pytest
import stbt_core as stbt


# Path to reference images directory
REFERENCE_IMAGES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "reference_images"
)


def get_reference_image(relative_path):
    """
    Get the full path to a reference image.

    Args:
        relative_path: Path relative to reference_images/ directory
                      (e.g., "epg/guide.png")

    Returns:
        Full path to the reference image
    """
    return os.path.join(REFERENCE_IMAGES_DIR, relative_path)


# Screen regions for common UI areas
class Regions:
    """Common screen regions for targeted operations."""

    # Full HD (1920x1080) regions - adjust as needed for your device
    HEADER = stbt.Region(x=0, y=0, width=1920, height=100)
    FOOTER = stbt.Region(x=0, y=980, width=1920, height=100)
    CENTER = stbt.Region(x=400, y=200, width=1120, height=680)
    LEFT_SIDEBAR = stbt.Region(x=0, y=100, width=300, height=880)
    RIGHT_SIDEBAR = stbt.Region(x=1620, y=100, width=300, height=880)

    # EPG specific regions
    EPG_CHANNEL_LIST = stbt.Region(x=0, y=150, width=400, height=800)
    EPG_PROGRAM_INFO = stbt.Region(x=400, y=150, width=1520, height=200)
    EPG_GRID = stbt.Region(x=400, y=350, width=1520, height=600)

    # Playback control regions
    PLAYBACK_CONTROLS = stbt.Region(x=600, y=900, width=720, height=150)
    PROGRESS_BAR = stbt.Region(x=200, y=950, width=1520, height=50)


# Remote control key mappings
class Keys:
    """Standard remote control key constants."""

    # Navigation
    UP = "KEY_UP"
    DOWN = "KEY_DOWN"
    LEFT = "KEY_LEFT"
    RIGHT = "KEY_RIGHT"
    OK = "KEY_OK"
    SELECT = "KEY_OK"
    BACK = "KEY_BACK"
    HOME = "KEY_HOME"
    MENU = "KEY_MENU"

    # EPG/Guide
    EPG = "KEY_EPG"
    GUIDE = "KEY_EPG"
    INFO = "KEY_INFO"

    # Playback
    PLAY = "KEY_PLAY"
    PAUSE = "KEY_PAUSE"
    PLAY_PAUSE = "KEY_PLAYPAUSE"
    STOP = "KEY_STOP"
    FAST_FORWARD = "KEY_FASTFORWARD"
    REWIND = "KEY_REWIND"
    RECORD = "KEY_RECORD"

    # Channel
    CHANNEL_UP = "KEY_CHANNELUP"
    CHANNEL_DOWN = "KEY_CHANNELDOWN"

    # Volume
    VOLUME_UP = "KEY_VOLUMEUP"
    VOLUME_DOWN = "KEY_VOLUMEDOWN"
    MUTE = "KEY_MUTE"

    # Numbers
    NUM_0 = "KEY_0"
    NUM_1 = "KEY_1"
    NUM_2 = "KEY_2"
    NUM_3 = "KEY_3"
    NUM_4 = "KEY_4"
    NUM_5 = "KEY_5"
    NUM_6 = "KEY_6"
    NUM_7 = "KEY_7"
    NUM_8 = "KEY_8"
    NUM_9 = "KEY_9"

    # Colors
    RED = "KEY_RED"
    GREEN = "KEY_GREEN"
    YELLOW = "KEY_YELLOW"
    BLUE = "KEY_BLUE"


# Helper functions
def navigate_to_home(timeout_secs=10):
    """
    Navigate to the home screen.

    Presses HOME key and waits for home screen to appear.
    """
    stbt.press(Keys.HOME)
    # Optionally wait for home screen image
    # stbt.wait_for_match(get_reference_image("common/home_screen.png"), timeout_secs=timeout_secs)


def open_epg(timeout_secs=10):
    """
    Open the Electronic Program Guide.

    Presses EPG key and waits for guide to appear.
    """
    stbt.press(Keys.EPG)
    # Optionally wait for EPG image
    # stbt.wait_for_match(get_reference_image("epg/guide.png"), timeout_secs=timeout_secs)


def close_epg():
    """Close the EPG guide by pressing BACK."""
    stbt.press(Keys.BACK)


def verify_video_playing(timeout_secs=5, region=None):
    """
    Verify that video is playing by detecting motion.

    Args:
        timeout_secs: How long to wait for motion
        region: Optional region to check for motion

    Returns:
        True if motion detected

    Raises:
        MotionTimeout if no motion detected
    """
    if region:
        stbt.wait_for_motion(timeout_secs=timeout_secs, region=region)
    else:
        stbt.wait_for_motion(timeout_secs=timeout_secs)
    return True


def verify_no_motion(duration_secs=2, region=None):
    """
    Verify that video is paused/frozen (no motion).

    Args:
        duration_secs: How long to check for absence of motion
        region: Optional region to check

    Returns:
        True if no motion detected for the duration
    """
    try:
        if region:
            stbt.wait_for_motion(timeout_secs=duration_secs, region=region)
        else:
            stbt.wait_for_motion(timeout_secs=duration_secs)
        return False  # Motion was detected
    except stbt.MotionTimeout:
        return True  # No motion - video is paused


def press_and_verify(key, expected_image, timeout_secs=5):
    """
    Press a key and verify expected image appears.

    Args:
        key: Remote key to press
        expected_image: Reference image path to wait for
        timeout_secs: Timeout for image to appear

    Returns:
        MatchResult from wait_for_match
    """
    stbt.press(key)
    return stbt.wait_for_match(expected_image, timeout_secs=timeout_secs)


def navigate_to_item(target_image, direction_key=Keys.DOWN, max_presses=20):
    """
    Navigate to an item by pressing direction key until target is found.

    Args:
        target_image: Reference image of target item
        direction_key: Key to press for navigation
        max_presses: Maximum number of key presses

    Returns:
        MatchResult when target is found

    Raises:
        Exception if target not found within max_presses
    """
    return stbt.press_until_match(direction_key, target_image, max_presses=max_presses)


def read_text_from_region(region, mode=None):
    """
    Read text from a screen region using OCR.

    Args:
        region: stbt.Region to read text from
        mode: Optional OCR mode

    Returns:
        Recognized text string
    """
    if mode:
        return stbt.ocr(region=region, mode=mode)
    return stbt.ocr(region=region)


# Pytest fixtures
@pytest.fixture
def keys():
    """Fixture providing access to key constants."""
    return Keys


@pytest.fixture
def regions():
    """Fixture providing access to common screen regions."""
    return Regions


@pytest.fixture
def at_home(request):
    """
    Fixture that ensures test starts from home screen.

    Navigates to home before test and optionally after.
    """
    navigate_to_home()
    yield
    # Optionally navigate back to home after test
    # navigate_to_home()


@pytest.fixture
def epg_open(request):
    """
    Fixture that opens EPG before test and closes it after.
    """
    open_epg()
    yield
    close_epg()


@pytest.fixture
def live_tv_playing():
    """
    Fixture that ensures live TV is playing before test.
    """
    # Press HOME then navigate to live TV
    navigate_to_home()
    # Optionally tune to a default channel
    # stbt.press(Keys.NUM_1)
    yield


# Custom assertions
def assert_image_visible(image_path, timeout_secs=5, region=None):
    """
    Assert that an image is visible on screen.

    Args:
        image_path: Path to reference image
        timeout_secs: How long to wait
        region: Optional region to search in
    """
    try:
        if region:
            result = stbt.wait_for_match(image_path, timeout_secs=timeout_secs, region=region)
        else:
            result = stbt.wait_for_match(image_path, timeout_secs=timeout_secs)
        assert result.match, f"Image {image_path} not found"
    except stbt.MatchTimeout:
        pytest.fail(f"Image {image_path} not found within {timeout_secs} seconds")


def assert_text_visible(expected_text, region, timeout_secs=5):
    """
    Assert that specific text is visible in a region.

    Args:
        expected_text: Text to look for
        region: Region to check
        timeout_secs: How long to wait
    """
    from stbt_core import wait_until

    def text_found():
        text = stbt.ocr(region=region)
        return expected_text in text

    assert wait_until(text_found, timeout_secs=timeout_secs), \
        f"Text '{expected_text}' not found in region {region}"
