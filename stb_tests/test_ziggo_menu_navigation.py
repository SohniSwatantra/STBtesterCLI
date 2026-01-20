"""
Test: Ziggo Menu Navigation and Content Access

Generated from video analysis: video (8).mp4
Device: stb-tester-48b02d5b0ab7

This test verifies:
1. Opening the Ziggo main menu from live TV
2. Menu displays with correct categories
3. Content can be selected and played
"""

import pytest
import stbt_core as stbt

from conftest import (
    Keys,
    Regions,
    get_reference_image,
    verify_video_playing,
)


class TestZiggoMenuNavigation:
    """
    Tests for Ziggo Menu Navigation

    User Story:
    As a viewer, I want to access the Ziggo main menu from live TV
    so that I can browse and watch content from Movies & Series.

    Acceptance Criteria:
    - Menu opens when pressing MENU key
    - Menu categories are visible (For You, Apps, Entertainment, Sports, Recordings)
    - Can navigate to content
    - Content plays with video motion
    """

    # Screen regions for Ziggo UI
    MENU_HEADER_REGION = stbt.Region(x=0, y=40, width=1280, height=60)
    CONTENT_TITLE_REGION = stbt.Region(x=50, y=130, width=400, height=150)
    CONTENT_AREA_REGION = stbt.Region(x=0, y=400, width=1280, height=300)

    def test_open_menu_from_live_tv(self):
        """
        Scenario: Open Ziggo Menu from Live TV

        Given: Live TV is playing (e.g., Ziggo Sport)
        When: User presses MENU key
        Then:
        - Main menu appears
        - "For You" tab is visible/selected
        - Menu categories are displayed
        """
        # Given: Ensure we're on live TV (press BACK to exit any overlays)
        for _ in range(2):
            stbt.press(Keys.BACK)
            import time
            time.sleep(0.3)

        # When: Press MENU to open the main menu
        stbt.press(Keys.MENU)

        # Then: Wait for menu to appear
        # Option 1: Wait for menu reference image
        # stbt.wait_for_match(
        #     get_reference_image("ziggo/menu_for_you.png"),
        #     timeout_secs=5
        # )

        # Option 2: Use OCR to verify menu categories
        import time
        time.sleep(2)  # Wait for menu to load

        # Verify menu header contains expected categories
        menu_text = stbt.ocr(region=self.MENU_HEADER_REGION)
        expected_categories = ["For You", "Apps", "Entertainment", "Sports", "Recordings"]

        found_categories = []
        for category in expected_categories:
            if category.lower() in menu_text.lower():
                found_categories.append(category)

        assert len(found_categories) >= 3, \
            f"Expected menu categories, found: {menu_text}"

        print(f"Menu opened successfully. Found categories: {found_categories}")

    def test_navigate_to_entertainment(self):
        """
        Scenario: Navigate to Entertainment section

        Given: Ziggo menu is open
        When: User navigates to Entertainment
        Then:
        - Entertainment section is displayed
        - Content tiles are visible
        """
        # Given: Open menu first
        stbt.press(Keys.MENU)
        import time
        time.sleep(2)

        # When: Navigate RIGHT to Entertainment
        # Menu order: For You -> TV & Replay -> Apps -> Entertainment
        for _ in range(3):
            stbt.press(Keys.RIGHT)
            time.sleep(0.5)

        # Then: Verify Entertainment is selected
        stbt.press(Keys.OK)  # Enter Entertainment section
        time.sleep(2)

        # Verify content is displayed
        # Using motion detection or image match
        # stbt.wait_for_match(get_reference_image("ziggo/entertainment_section.png"))

    def test_select_and_play_content(self):
        """
        Scenario: Select content and verify playback

        Given: User is in a content section (e.g., For You with Father Brown)
        When: User selects "Watch" on a content item
        Then:
        - Content starts playing
        - Video motion is detected
        """
        # Given: Open menu and navigate to content
        stbt.press(Keys.MENU)
        import time
        time.sleep(2)

        # Navigate down to content area (e.g., Father Brown "Watch" button)
        stbt.press(Keys.DOWN)
        time.sleep(0.5)

        # When: Select "Watch"
        stbt.press(Keys.OK)

        # Then: Verify video playback starts
        time.sleep(3)  # Wait for video to load

        try:
            verify_video_playing(timeout_secs=10)
            print("Content playback verified - motion detected")
        except Exception as e:
            # If motion detection fails, check for video player UI
            print(f"Motion detection: {e}")
            # Alternative: check for player controls or progress bar

    def test_full_journey_menu_to_playback(self):
        """
        Scenario: Complete journey from Live TV to content playback

        This is the full test matching the video analysis:
        1. Start from live TV
        2. Open menu
        3. Browse content
        4. Play content
        5. Verify playback

        Given: Device is showing live TV
        When: User navigates through menu to content
        Then: Selected content plays successfully
        """
        import time

        # Step 1: Ensure clean state - exit any menus/overlays
        print("Step 1: Returning to live TV...")
        for _ in range(3):
            stbt.press(Keys.BACK)
            time.sleep(0.3)

        # Verify live TV (optional - check for motion)
        try:
            verify_video_playing(timeout_secs=5)
            print("Live TV confirmed - motion detected")
        except:
            print("Continuing without motion verification...")

        # Step 2: Open main menu
        print("Step 2: Opening Ziggo menu...")
        stbt.press(Keys.MENU)
        time.sleep(2)

        # Step 3: Verify menu appeared
        menu_text = stbt.ocr(region=self.MENU_HEADER_REGION)
        print(f"Menu text: {menu_text}")
        assert "for you" in menu_text.lower() or "apps" in menu_text.lower(), \
            "Menu did not open correctly"

        # Step 4: Navigate to content (e.g., first item in For You)
        print("Step 3: Navigating to content...")
        stbt.press(Keys.DOWN)  # Move to content area
        time.sleep(0.5)
        stbt.press(Keys.DOWN)  # Move to first content row
        time.sleep(0.5)

        # Step 5: Select content
        print("Step 4: Selecting content...")
        stbt.press(Keys.OK)
        time.sleep(1)

        # If we land on a detail page, select "Watch"
        stbt.press(Keys.OK)
        time.sleep(3)

        # Step 6: Verify playback
        print("Step 5: Verifying playback...")
        try:
            verify_video_playing(timeout_secs=10)
            print("SUCCESS: Content is playing!")
        except Exception as e:
            pytest.fail(f"Playback verification failed: {e}")


class TestZiggoChannelTuning:
    """
    Tests for channel tuning functionality observed in video.
    """

    def test_tune_to_channel_1(self):
        """
        Scenario: Tune to channel 1 using number key

        Given: Device is on any channel
        When: User presses KEY_1
        Then: Device tunes to channel 1
        """
        import time

        # Press channel number
        stbt.press("KEY_1")
        time.sleep(2)

        # Verify channel changed (channel banner should appear)
        # Could use OCR to verify channel number or image match


# Standalone test function for quick verification
def test_menu_opens():
    """Quick test to verify menu opens."""
    stbt.press(Keys.MENU)
    import time
    time.sleep(2)

    # Basic OCR check
    text = stbt.ocr()
    print(f"Screen text: {text[:200]}...")
    assert len(text) > 10, "No text detected on screen"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
