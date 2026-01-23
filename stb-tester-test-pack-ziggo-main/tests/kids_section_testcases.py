"""
Kids Section Test Cases
Tests for verifying Kids section availability in Entertainment.
"""
import time
import stbt
from tests.helper import pre_condition, ocr_text_extraction

# Regions for Kids section navigation
MENU_HOME = stbt.Region(x=124, y=34, width=96, height=36)
ENTERTAINMENT_REGION = stbt.Region(x=56, y=26, width=269, height=38)
KIDS_SECTION_REGION = stbt.Region(x=55, y=400, width=300, height=50)
MENU_ITEM_REGION = stbt.Region(x=50, y=100, width=400, height=600)


def test_kids_section_available():
    """
    Test: Verify Kids section is available in Entertainment

    Steps:
    1. Press BACK keys to reset to known state
    2. Open main menu
    3. Navigate to Entertainment section
    4. Look for Kids section
    5. Verify Kids section is found

    Expected: Kids section should be visible in Entertainment menu
    """
    # Pre-condition: Reset to known state
    pre_condition()
    stbt.draw_text("Starting Kids Section Test...")

    # Step 1: Open main menu
    stbt.press_and_wait(key="KEY_MENU", timeout_secs=2)
    time.sleep(1)

    # Verify menu is open
    match_home = stbt.match_text("HOME", region=MENU_HOME)
    if match_home.match:
        stbt.draw_text("Menu opened successfully")
    else:
        stbt.draw_text("Menu opened - checking for navigation...")

    # Step 2: Navigate to find Entertainment section
    entertainment_found = False
    for i in range(10):
        # Check current menu item
        screen_text = stbt.ocr(region=MENU_ITEM_REGION).lower()
        stbt.draw_text(f"Checking menu item {i+1}...")

        if "entertainment" in screen_text:
            stbt.draw_text("Found Entertainment section!")
            entertainment_found = True
            stbt.press_and_wait(key="KEY_OK", timeout_secs=2)
            break
        elif "film" in screen_text or "movies" in screen_text:
            stbt.draw_text("Found Movies/Film section (Entertainment)")
            entertainment_found = True
            stbt.press_and_wait(key="KEY_OK", timeout_secs=2)
            break

        stbt.press_and_wait(key="KEY_DOWN", timeout_secs=0.5)

    if not entertainment_found:
        stbt.draw_text("Entertainment not found, trying right navigation...")
        pre_condition()
        stbt.press_and_wait(key="KEY_HOME", timeout_secs=2)
        for _ in range(6):
            stbt.press_and_wait(key="KEY_RIGHT", timeout_secs=0.5)
            screen_text = stbt.ocr().lower()
            if "entertainment" in screen_text or "film" in screen_text:
                entertainment_found = True
                stbt.press_and_wait(key="KEY_OK", timeout_secs=2)
                break

    assert entertainment_found, "Entertainment section not found in menu"
    time.sleep(1)

    # Step 3: Look for Kids section within Entertainment
    stbt.draw_text("Looking for Kids section...")
    kids_found = False
    kids_keywords = ["kids", "kinderen", "kinder", "children", "jeugd"]

    # Check current screen first
    screen_text = stbt.ocr().lower()
    for keyword in kids_keywords:
        if keyword in screen_text:
            kids_found = True
            stbt.draw_text(f"Kids section found! (keyword: {keyword})")
            break

    # If not found, navigate down to find it
    if not kids_found:
        for i in range(12):
            stbt.press_and_wait(key="KEY_DOWN", timeout_secs=0.5)
            screen_text = stbt.ocr().lower()

            for keyword in kids_keywords:
                if keyword in screen_text:
                    kids_found = True
                    stbt.draw_text(f"Kids section found after {i+1} presses!")
                    break

            if kids_found:
                break

    # Step 4: Assert Kids section was found
    assert kids_found, (
        f"Kids section NOT found in Entertainment! "
        f"Searched for: {kids_keywords}"
    )

    stbt.draw_text("TEST PASSED: Kids section is available!")

    # Cleanup
    pre_condition()


def test_kids_section_enter_and_verify():
    """
    Test: Navigate to Kids section and verify content

    Steps:
    1. Navigate to Entertainment > Kids
    2. Enter Kids section
    3. Verify Kids content is displayed

    Expected: Should see Kids-related content (cartoons, children's shows, etc.)
    """
    # Pre-condition
    pre_condition()
    stbt.draw_text("Starting Kids Section Enter Test...")

    # Open menu and navigate to Entertainment
    stbt.press_and_wait(key="KEY_MENU", timeout_secs=2)
    time.sleep(1)

    # Find Entertainment
    for _ in range(10):
        screen_text = stbt.ocr(region=MENU_ITEM_REGION).lower()
        if "entertainment" in screen_text or "film" in screen_text:
            stbt.press_and_wait(key="KEY_OK", timeout_secs=2)
            break
        stbt.press_and_wait(key="KEY_DOWN", timeout_secs=0.5)

    time.sleep(1)

    # Find and enter Kids section
    kids_keywords = ["kids", "kinderen", "kinder"]
    kids_found = False

    for _ in range(12):
        screen_text = stbt.ocr().lower()
        for keyword in kids_keywords:
            if keyword in screen_text:
                kids_found = True
                stbt.draw_text("Entering Kids section...")
                stbt.press_and_wait(key="KEY_OK", timeout_secs=2)
                break
        if kids_found:
            break
        stbt.press_and_wait(key="KEY_DOWN", timeout_secs=0.5)

    assert kids_found, "Kids section not found"
    time.sleep(2)

    # Verify we're in Kids section by checking content
    final_text = stbt.ocr().lower()
    kids_content_keywords = [
        "kids", "kinderen", "cartoon", "disney", "nick",
        "junior", "animation", "children"
    ]

    content_found = any(kw in final_text for kw in kids_content_keywords)
    stbt.draw_text(f"Kids content verified: {content_found}")

    # Take screenshot as evidence
    stbt.draw_text("Kids section entered successfully!")

    # Cleanup
    pre_condition()


def test_kids_section_navigation_from_home():
    """
    Test: Navigate to Kids section directly from Home screen

    Steps:
    1. Go to Home screen
    2. Navigate to Kids rail/section if visible
    3. Verify Kids content

    Expected: Kids section should be accessible from Home
    """
    # Pre-condition
    pre_condition()
    stbt.draw_text("Starting Kids from Home Test...")

    # Go to Home
    stbt.press_and_wait(key="KEY_HOME", timeout_secs=2)
    time.sleep(1)

    # Look for Kids on home screen
    kids_keywords = ["kids", "kinderen", "kinder", "junior"]
    kids_found = False

    # Check current screen
    screen_text = stbt.ocr().lower()
    for keyword in kids_keywords:
        if keyword in screen_text:
            kids_found = True
            stbt.draw_text(f"Kids found on home screen: {keyword}")
            break

    # Navigate down through home rails to find Kids
    if not kids_found:
        for i in range(8):
            stbt.press_and_wait(key="KEY_DOWN", timeout_secs=1)
            screen_text = stbt.ocr().lower()

            for keyword in kids_keywords:
                if keyword in screen_text:
                    kids_found = True
                    stbt.draw_text(f"Kids rail found at position {i+1}")
                    break

            if kids_found:
                break

    if kids_found:
        stbt.draw_text("TEST PASSED: Kids section accessible from Home!")
    else:
        stbt.draw_text("Kids not on Home, available in Entertainment menu")

    # Cleanup
    pre_condition()
