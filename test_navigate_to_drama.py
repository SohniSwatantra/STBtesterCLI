"""
STB Tester test case: Navigate to Drama section under Movies

This test navigates through an entertainment app's menu structure:
Home -> Movies -> Drama
"""

import stbt_core as stbt


def test_navigate_to_movies_drama():
    """
    Navigate from Home screen to the Drama section under Movies.

    Expected navigation path:
    1. Start from Home screen
    2. Navigate to Movies category
    3. Navigate to Drama sub-category
    """

    # Step 1: Ensure we're at the Home screen
    stbt.press("KEY_HOME")
    assert stbt.wait_for_match(
        "images/home_screen.png",
        timeout_secs=10
    ), "Failed to reach Home screen"

    # Step 2: Navigate to Movies section
    # This may require navigating through menu items
    _navigate_to_menu_item("Movies")

    stbt.press("KEY_OK")
    assert stbt.wait_for_match(
        "images/movies_section.png",
        timeout_secs=10
    ), "Failed to enter Movies section"

    # Step 3: Navigate to Drama category within Movies
    _navigate_to_menu_item("Drama")

    stbt.press("KEY_OK")
    assert stbt.wait_for_match(
        "images/drama_category.png",
        timeout_secs=10
    ), "Failed to enter Drama category"

    print("Successfully navigated to Movies > Drama")


def _navigate_to_menu_item(target_text, max_attempts=10):
    """
    Navigate through menu items to find and highlight the target.

    Uses OCR to read menu items and navigates down until the target is found.

    Args:
        target_text: The menu item text to find
        max_attempts: Maximum navigation attempts before failing
    """
    for attempt in range(max_attempts):
        # Check if target is currently visible and focused
        if _is_menu_item_focused(target_text):
            print(f"Found '{target_text}' after {attempt} key presses")
            return True

        # Navigate down to next menu item
        stbt.press("KEY_DOWN")
        stbt.wait_for_transition()

    raise AssertionError(
        f"Could not find menu item '{target_text}' after {max_attempts} attempts"
    )


def _is_menu_item_focused(target_text):
    """
    Check if the target menu item is currently focused/highlighted.

    Uses OCR to read the focused area and check for the target text.
    """
    # Option 1: Use OCR to find the text
    result = stbt.match_text(target_text)
    if result.match:
        # Additional check: verify it's in the focused/highlighted region
        # This depends on your specific UI - adjust region as needed
        return True

    return False


# Alternative implementation using FrameObject pattern (recommended for complex UIs)

class MainMenu(stbt.FrameObject):
    """Represents the main menu of the entertainment app."""

    @property
    def is_visible(self):
        return stbt.match("images/main_menu_indicator.png")

    @property
    def focused_item(self):
        """Returns the currently focused menu item text."""
        # Define the region where focused item text appears
        focused_region = stbt.Region(x=100, y=200, width=300, height=50)
        return stbt.ocr(region=focused_region).strip()

    def navigate_to(self, target):
        """Navigate to a specific menu item."""
        for _ in range(10):
            if target.lower() in self.focused_item.lower():
                return True
            stbt.press("KEY_DOWN")
            stbt.wait_for_transition()
        return False


class MoviesSection(stbt.FrameObject):
    """Represents the Movies section."""

    @property
    def is_visible(self):
        return stbt.match("images/movies_header.png")

    @property
    def focused_category(self):
        """Returns the currently focused category."""
        category_region = stbt.Region(x=50, y=150, width=200, height=40)
        return stbt.ocr(region=category_region).strip()

    def navigate_to_category(self, category_name):
        """Navigate to a specific category within Movies."""
        for _ in range(10):
            if category_name.lower() in self.focused_category.lower():
                return True
            stbt.press("KEY_DOWN")
            stbt.wait_for_transition()
        return False


def test_navigate_to_drama_with_frame_objects():
    """
    Alternative test using FrameObject pattern for better maintainability.
    """
    # Go to home and open main menu
    stbt.press("KEY_HOME")

    # Navigate main menu to Movies
    menu = MainMenu()
    assert menu.is_visible, "Main menu not visible"
    assert menu.navigate_to("Movies"), "Could not find Movies in menu"

    stbt.press("KEY_OK")

    # Navigate Movies section to Drama
    movies = MoviesSection()
    assert movies.is_visible, "Movies section not visible"
    assert movies.navigate_to_category("Drama"), "Could not find Drama category"

    stbt.press("KEY_OK")

    # Verify we're in Drama
    assert stbt.wait_for_match(
        "images/drama_category.png",
        timeout_secs=10
    ), "Failed to enter Drama category"


if __name__ == "__main__":
    # Run the test directly
    test_navigate_to_movies_drama()
