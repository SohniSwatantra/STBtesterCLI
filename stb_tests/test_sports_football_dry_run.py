"""
Dry-run version of sports football test for local validation.

This demonstrates the test logic without requiring stbt-core hardware dependencies.
Run with: python stb_tests/test_sports_football_dry_run.py
"""

import time


# Mock stbt_core for dry-run
class MockStbt:
    """Mock STB Tester core for dry-run testing."""

    class Region:
        def __init__(self, x=0, y=0, width=1280, height=720):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        def __repr__(self):
            return f"Region(x={self.x}, y={self.y}, w={self.width}, h={self.height})"

    @staticmethod
    def press(key):
        print(f"  [PRESS] {key}")

    @staticmethod
    def ocr(region=None):
        """Simulated OCR responses based on test flow."""
        if not hasattr(MockStbt, '_ocr_call_count'):
            MockStbt._ocr_call_count = 0
        MockStbt._ocr_call_count += 1

        # Simulate menu navigation responses
        responses = {
            1: "For You  Apps  Entertainment",
            2: "Apps  Entertainment  Sports",
            3: "Entertainment  Sports  Recordings",
            4: "Sports  Recordings  Search",
            5: "Football  Tennis  Racing  Live",
            6: "Football  Tennis  Racing",
            7: "Premier League  Serie A  La Liga",
            8: "AC Milan vs Napoli  19:00",
            9: "Napoli vs Juventus  Live Now",
            10: "Napoli  SSC Napoli  Serie A",
        }
        response = responses.get(MockStbt._ocr_call_count, "Napoli vs Inter  21:00")
        print(f"  [OCR] Region: {region} -> '{response}'")
        return response

    @staticmethod
    def wait_for_motion(timeout_secs=5, region=None):
        print(f"  [MOTION] Waiting for motion (timeout={timeout_secs}s)")


# Mock keys
class Keys:
    UP = "KEY_UP"
    DOWN = "KEY_DOWN"
    LEFT = "KEY_LEFT"
    RIGHT = "KEY_RIGHT"
    OK = "KEY_OK"
    BACK = "KEY_BACK"
    MENU = "KEY_MENU"


def test_navigate_to_sports_and_find_napoli_match():
    """
    DRY RUN: Navigate to Sports > Football and find Napoli match

    Given: Device is at home/live TV
    When: User navigates to Sports in top nav bar
    And: User navigates to Football option
    Then: Napoli match should be visible in listings
    """
    stbt = MockStbt()
    TOP_NAV_REGION = MockStbt.Region(x=0, y=40, width=1280, height=60)
    SUB_NAV_REGION = MockStbt.Region(x=0, y=100, width=1280, height=60)
    CONTENT_AREA_REGION = MockStbt.Region(x=0, y=160, width=1280, height=560)

    print("\n" + "="*60)
    print("DRY RUN: test_navigate_to_sports_and_find_napoli_match")
    print("="*60)

    # Setup: Exit any overlays
    print("\nSetup: Exiting any overlays...")
    for _ in range(2):
        stbt.press(Keys.BACK)
        time.sleep(0.1)

    # Step 1: Open main menu
    print("\nStep 1: Opening main menu...")
    stbt.press(Keys.MENU)
    time.sleep(0.2)

    # Step 2: Navigate to Sports in top nav bar
    print("\nStep 2: Navigating to Sports in top nav bar...")
    sports_found = False
    for i in range(6):
        nav_text = stbt.ocr(region=TOP_NAV_REGION)
        if "sports" in nav_text.lower():
            print(f"  -> Sports found after {i} RIGHT presses")
            sports_found = True
            break
        stbt.press(Keys.RIGHT)
        time.sleep(0.1)

    if not sports_found:
        print("  [FAIL] Could not navigate to Sports")
        return False

    # Step 3: Enter Sports section
    print("\nStep 3: Entering Sports section...")
    stbt.press(Keys.OK)
    time.sleep(0.2)

    # Step 4: Navigate to Football
    print("\nStep 4: Navigating to Football...")
    stbt.press(Keys.DOWN)
    time.sleep(0.1)

    football_found = False
    for i in range(5):
        screen_text = stbt.ocr(region=SUB_NAV_REGION)
        if "football" in screen_text.lower():
            print(f"  -> Football found after {i} navigations")
            football_found = True
            stbt.press(Keys.OK)
            break
        stbt.press(Keys.RIGHT)
        time.sleep(0.1)

    if not football_found:
        print("  [FAIL] Could not find Football option")
        return False

    # Step 5: Search for Napoli match
    print("\nStep 5: Searching for Napoli match...")
    napoli_found = False
    for i in range(10):
        content_text = stbt.ocr(region=CONTENT_AREA_REGION)
        if "napoli" in content_text.lower():
            print(f"  -> Napoli found after {i} scrolls!")
            napoli_found = True
            break
        stbt.press(Keys.DOWN)
        time.sleep(0.1)

    # Result
    print("\n" + "="*60)
    if napoli_found:
        print("RESULT: PASS - Napoli match found in Football listings")
    else:
        print("RESULT: FAIL - Napoli match not found")
    print("="*60 + "\n")

    return napoli_found


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# STB Tester Dry Run - Sports Football Test")
    print("# This simulates the test flow without real hardware")
    print("#"*60)

    success = test_navigate_to_sports_and_find_napoli_match()
    exit(0 if success else 1)
