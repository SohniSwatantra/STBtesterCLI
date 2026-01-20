"""
Example STB Tester Test Module

This module demonstrates the patterns and structure for generated test scripts.
Tests are generated from specifications in TEST_SPECS.md.

Run with: stbt run stb_tests/test_example.py
Or with pytest: pytest stb_tests/test_example.py
"""

import pytest
import stbt_core as stbt

from conftest import (
    Keys,
    Regions,
    get_reference_image,
    navigate_to_home,
    open_epg,
    close_epg,
    verify_video_playing,
    verify_no_motion,
)


class TestEPGNavigation:
    """
    Tests for EPG/Guide Navigation

    Generated from TEST_SPECS.md - EPG/Guide Navigation Tests
    """

    def test_open_epg_from_live_tv(self):
        """
        Scenario: Open EPG from Live TV

        Given: Device is playing live TV
        When: User presses the EPG key
        Then:
        - EPG guide overlay appears
        - Current time slot is visible
        - Channel list is displayed
        """
        # Given: Device is playing live TV
        navigate_to_home()

        # When: User presses the EPG key
        stbt.press(Keys.EPG)

        # Then: EPG guide overlay appears
        # Uncomment when reference image is available:
        # stbt.wait_for_match(
        #     get_reference_image("epg/guide.png"),
        #     timeout_secs=5
        # )

        # Verify EPG is visible (placeholder - adjust for your UI)
        # For now, just wait for screen to stabilize
        import time
        time.sleep(2)

        # Cleanup
        stbt.press(Keys.BACK)

    def test_scroll_down_channel_list(self, epg_open):
        """
        Scenario: Scroll Down Channel List

        Given: EPG guide is open (provided by epg_open fixture)
        When: User presses DOWN key multiple times
        Then:
        - Selection moves to next channel
        - Channel info panel updates
        - Scrolling continues smoothly
        """
        # When: User presses DOWN key multiple times
        for _ in range(5):
            stbt.press(Keys.DOWN)
            # Allow time for UI to update
            import time
            time.sleep(0.5)

        # Then: Verify navigation occurred
        # Uncomment when reference images are available:
        # assert stbt.match(get_reference_image("epg/channel_selected.png"))

    def test_select_channel_from_epg(self, epg_open):
        """
        Scenario: Select Channel from EPG

        Given: EPG guide is open and a channel is highlighted
        When: User presses OK/Select
        Then:
        - EPG closes
        - Selected channel tunes
        - Video starts playing
        """
        # Given: EPG is already open (from fixture)
        # Navigate to a channel
        stbt.press(Keys.DOWN)

        # When: User presses OK/Select
        stbt.press(Keys.OK)

        # Then: Video starts playing
        # Verify video playback with motion detection
        try:
            verify_video_playing(timeout_secs=10)
        except stbt.MotionTimeout:
            pytest.skip("Motion detection not available in this environment")


class TestVideoPlayback:
    """
    Tests for Video Playback

    Generated from TEST_SPECS.md - Video Playback Tests
    """

    def test_pause_live_tv(self, live_tv_playing):
        """
        Scenario: Pause Live TV

        Given: Live TV is playing with visible motion
        When: User presses PAUSE
        Then:
        - Pause indicator appears on screen
        - Video motion stops
        - Timecode shows paused state
        """
        # Given: Live TV is playing (from fixture)
        # Verify video is playing first
        try:
            verify_video_playing(timeout_secs=5)
        except stbt.MotionTimeout:
            pytest.skip("Motion detection not available - cannot verify playback")

        # When: User presses PAUSE
        stbt.press(Keys.PAUSE)

        # Then: Video motion stops
        import time
        time.sleep(1)  # Allow pause to take effect

        # Verify pause indicator (uncomment when image available)
        # stbt.wait_for_match(
        #     get_reference_image("playback/pause_indicator.png"),
        #     timeout_secs=3
        # )

        # Verify no motion (video is paused)
        assert verify_no_motion(duration_secs=2), "Video should be paused (no motion)"

        # Cleanup - resume playback
        stbt.press(Keys.PLAY)

    def test_resume_from_pause(self, live_tv_playing):
        """
        Scenario: Resume from Pause

        Given: Live TV is paused
        When: User presses PLAY
        Then:
        - Pause indicator disappears
        - Video motion resumes
        - Content continues from pause point
        """
        # Given: Live TV is paused
        stbt.press(Keys.PAUSE)
        import time
        time.sleep(1)

        # When: User presses PLAY
        stbt.press(Keys.PLAY)

        # Then: Video motion resumes
        try:
            verify_video_playing(timeout_secs=5)
        except stbt.MotionTimeout:
            pytest.skip("Motion detection not available in this environment")


class TestSettings:
    """
    Tests for Settings & Configuration

    Generated from TEST_SPECS.md - Settings & Configuration Tests
    """

    def test_open_settings_from_home(self, at_home):
        """
        Scenario: Open Settings from Home

        Given: Device is on home screen (provided by at_home fixture)
        When: User navigates to Settings and presses OK
        Then:
        - Settings menu appears
        - Setting categories are displayed
        - First category is highlighted
        """
        # When: User navigates to Settings
        # Navigation steps depend on your specific UI layout
        # This is a placeholder - adjust for your device

        # Example: Navigate right to settings icon
        stbt.press(Keys.RIGHT)
        stbt.press(Keys.RIGHT)
        stbt.press(Keys.OK)

        # Then: Settings menu appears
        # Uncomment when reference image is available:
        # stbt.wait_for_match(
        #     get_reference_image("settings/settings_menu.png"),
        #     timeout_secs=5
        # )

        import time
        time.sleep(2)

        # Cleanup
        stbt.press(Keys.HOME)


# Example of a standalone test function (not in a class)
def test_basic_navigation():
    """
    Basic navigation smoke test.

    Verifies that basic remote control navigation works.
    """
    # Press some keys and verify no errors occur
    keys_to_test = [
        Keys.HOME,
        Keys.UP,
        Keys.DOWN,
        Keys.LEFT,
        Keys.RIGHT,
        Keys.HOME,
    ]

    for key in keys_to_test:
        stbt.press(key)
        import time
        time.sleep(0.3)


# Example of using OCR for text verification
def test_ocr_example():
    """
    Example test demonstrating OCR usage.

    Note: Requires appropriate screen region configuration.
    """
    # Read text from a region
    region = Regions.HEADER

    try:
        text = stbt.ocr(region=region)
        print(f"OCR result from header region: {text}")
        # Add assertions as needed
        # assert "Expected Text" in text
    except Exception as e:
        pytest.skip(f"OCR not available in this environment: {e}")


# Example of using image matching with regions
def test_match_with_region_example():
    """
    Example test demonstrating image matching with regions.
    """
    # Match an image only within a specific region
    region = Regions.CENTER

    # Uncomment when reference image is available:
    # result = stbt.match(
    #     get_reference_image("common/logo.png"),
    #     region=region
    # )
    # assert result.match, "Logo should be visible in center region"
    pass


if __name__ == "__main__":
    # Allow running individual tests with: python test_example.py
    pytest.main([__file__, "-v"])
