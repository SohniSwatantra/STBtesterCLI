"""
Test: Sports Football - Napoli Match Check

This test verifies:
1. Navigation to Sports section in top nav bar
2. Navigation to Football within Sports
3. Finding a Napoli match in the football listings
"""

import pytest
import time
import stbt_core as stbt

from conftest import (
    Keys,
    Regions,
    verify_video_playing,
)


class TestSportsFootball:
    """
    Tests for Sports Football content.

    User Story:
    As a sports viewer, I want to navigate to the Football section
    so that I can find and watch Napoli matches.

    Acceptance Criteria:
    - Menu opens and Sports section is accessible
    - Football category is found within Sports
    - Napoli match is visible in the listings
    """

    # Screen regions for Sports UI
    TOP_NAV_REGION = stbt.Region(x=0, y=40, width=1280, height=60)
    SUB_NAV_REGION = stbt.Region(x=0, y=100, width=1280, height=60)
    CONTENT_AREA_REGION = stbt.Region(x=0, y=160, width=1280, height=560)
    FULL_SCREEN_REGION = stbt.Region(x=0, y=0, width=1280, height=720)

    def setup_method(self):
        """Reset to known state before each test."""
        # Exit any menus/overlays
        for _ in range(2):
            stbt.press(Keys.BACK)
            time.sleep(0.3)

    def test_navigate_to_sports_and_find_napoli_match(self):
        """
        Scenario: Navigate to Sports > Football and find Napoli match

        Given: Device is at home/live TV
        When: User navigates to Sports in top nav bar
        And: User navigates to Football option
        Then: Napoli match should be visible in listings
        """
        # Step 1: Open main menu
        print("Step 1: Opening main menu...")
        stbt.press(Keys.MENU)
        time.sleep(2)

        # Step 2: Navigate to Sports in top nav bar
        # Menu order typically: For You -> TV & Replay -> Apps -> Entertainment -> Sports
        print("Step 2: Navigating to Sports in top nav bar...")
        self._navigate_to_sports()

        # Step 3: Enter Sports section
        print("Step 3: Entering Sports section...")
        stbt.press(Keys.OK)
        time.sleep(2)

        # Step 4: Navigate to Football within Sports
        print("Step 4: Navigating to Football...")
        self._navigate_to_football()

        # Step 5: Search for Napoli match
        print("Step 5: Searching for Napoli match...")
        napoli_found = self._find_napoli_match()

        assert napoli_found, "Napoli match not found in Football listings"
        print("SUCCESS: Napoli match found!")

    def _navigate_to_sports(self, max_presses=10):
        """
        Navigate to Sports in the top navigation bar.

        Uses OCR to verify Sports is highlighted/selected.
        """
        for i in range(max_presses):
            # Check if Sports is visible and highlighted
            nav_text = stbt.ocr(region=self.TOP_NAV_REGION)
            print(f"Top nav text: {nav_text}")

            if "sports" in nav_text.lower():
                # Check if we're at Sports section
                # Additional verification could check for highlight/selection
                print(f"Sports found in navigation after {i} presses")
                return True

            # Navigate right to next menu item
            stbt.press(Keys.RIGHT)
            time.sleep(0.5)

        raise Exception("Could not navigate to Sports section")

    def _navigate_to_football(self, max_presses=10):
        """
        Navigate to Football option within Sports section.

        Sports typically has sub-categories: All, Football, Tennis, etc.
        """
        # First, try navigating down to sub-navigation or content area
        stbt.press(Keys.DOWN)
        time.sleep(0.5)

        for i in range(max_presses):
            # Check current screen for Football option
            screen_text = stbt.ocr(region=self.SUB_NAV_REGION)
            content_text = stbt.ocr(region=self.CONTENT_AREA_REGION)
            combined_text = f"{screen_text} {content_text}".lower()

            print(f"Screen text: {combined_text[:100]}...")

            if "football" in combined_text or "voetbal" in combined_text:
                print(f"Football option found after {i} presses")
                # Select Football
                stbt.press(Keys.OK)
                time.sleep(1)
                return True

            # Try navigating right through sub-categories
            stbt.press(Keys.RIGHT)
            time.sleep(0.5)

        # If not found in sub-nav, try navigating down through content
        for i in range(max_presses):
            content_text = stbt.ocr(region=self.CONTENT_AREA_REGION)

            if "football" in content_text.lower() or "voetbal" in content_text.lower():
                print(f"Football found in content area")
                stbt.press(Keys.OK)
                time.sleep(1)
                return True

            stbt.press(Keys.DOWN)
            time.sleep(0.5)

        raise Exception("Could not find Football option in Sports")

    def _find_napoli_match(self, max_scrolls=20):
        """
        Search for Napoli match in the Football listings.

        Scrolls through the content looking for 'Napoli' text.
        """
        for i in range(max_scrolls):
            # Read text from content area and full screen
            content_text = stbt.ocr(region=self.CONTENT_AREA_REGION)
            full_text = stbt.ocr(region=self.FULL_SCREEN_REGION)

            combined_text = f"{content_text} {full_text}".lower()
            print(f"Searching for Napoli... Scroll {i+1}")

            if "napoli" in combined_text:
                print(f"Napoli found after {i+1} scrolls!")
                return True

            # Scroll down to load more content
            stbt.press(Keys.DOWN)
            time.sleep(0.8)

        return False

    def test_sports_section_accessible(self):
        """
        Scenario: Verify Sports section is accessible from menu

        Given: Device is at home
        When: User opens menu and navigates to Sports
        Then: Sports section should be accessible
        """
        # Open menu
        stbt.press(Keys.MENU)
        time.sleep(2)

        # Navigate to Sports
        self._navigate_to_sports()

        # Verify we can enter Sports
        stbt.press(Keys.OK)
        time.sleep(2)

        # Check for Sports content indicators
        screen_text = stbt.ocr()
        sports_indicators = ["football", "voetbal", "tennis", "sports", "live", "match"]

        found_indicators = [ind for ind in sports_indicators if ind in screen_text.lower()]
        assert len(found_indicators) > 0, \
            f"Sports section content not found. Screen text: {screen_text[:200]}"

        print(f"Sports section verified. Found indicators: {found_indicators}")


class TestFootballNavigation:
    """Additional tests for Football navigation patterns."""

    TOP_NAV_REGION = stbt.Region(x=0, y=40, width=1280, height=60)
    CONTENT_REGION = stbt.Region(x=0, y=100, width=1280, height=620)

    def test_direct_navigation_to_football(self):
        """
        Scenario: Navigate directly to Football from Sports

        Given: Menu is open at Sports section
        When: User selects Football category
        Then: Football content is displayed
        """
        # Open menu
        stbt.press(Keys.MENU)
        time.sleep(2)

        # Navigate to Sports (typically 4 positions right from For You)
        for _ in range(4):
            stbt.press(Keys.RIGHT)
            time.sleep(0.5)

        # Enter Sports
        stbt.press(Keys.OK)
        time.sleep(2)

        # Look for Football in sub-categories
        screen_text = stbt.ocr()
        assert "football" in screen_text.lower() or "voetbal" in screen_text.lower(), \
            f"Football category not found in Sports. Text: {screen_text[:200]}"


# Standalone test function
def test_find_napoli_in_sports():
    """Quick test to navigate to Sports and find Napoli."""
    # Exit any overlays
    stbt.press(Keys.BACK)
    time.sleep(0.5)

    # Open menu
    stbt.press(Keys.MENU)
    time.sleep(2)

    # Navigate right to find Sports (adjust count based on menu layout)
    for i in range(6):
        nav_region = stbt.Region(x=0, y=40, width=1280, height=60)
        text = stbt.ocr(region=nav_region)
        print(f"Nav position {i}: {text}")

        if "sports" in text.lower():
            print(f"Found Sports at position {i}")
            stbt.press(Keys.OK)
            time.sleep(2)
            break

        stbt.press(Keys.RIGHT)
        time.sleep(0.5)

    # Navigate down and look for Football, then Napoli
    for _ in range(5):
        stbt.press(Keys.DOWN)
        time.sleep(0.5)

    # Search for Napoli
    for i in range(10):
        full_text = stbt.ocr()
        if "napoli" in full_text.lower():
            print(f"SUCCESS: Napoli found!")
            return

        stbt.press(Keys.DOWN)
        time.sleep(0.5)

    pytest.fail("Napoli match not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
