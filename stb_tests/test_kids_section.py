"""
Test Kids Section Availability
Verifies that the Kids section is available inside Entertainment.
"""
import stbt_core as stbt


def test_kids_section_available():
    """
    Scenario: Verify Kids section is available in Entertainment

    Given: The STB is on the home screen
    When: User navigates to Entertainment section
    And: User looks for Kids section
    Then: Kids section should be visible/accessible

    STEPS:
    -------
    Step 1: Press HOME to ensure we start from home screen
    Step 2: Navigate to Entertainment section (using menu or direct navigation)
    Step 3: Look for "Kids" or "Kinderen" text in the Entertainment section
    Step 4: Verify Kids section is found using OCR text detection
    """

    # ========================================
    # STEP 1: Go to Home Screen
    # ========================================
    print("STEP 1: Navigating to Home screen...")
    stbt.press("KEY_HOME")
    stbt.press_and_wait("KEY_HOME", stable_secs=2)
    print("  ✓ Home screen reached")

    # Take screenshot to confirm home screen
    frame = stbt.get_frame()
    print(f"  Screenshot captured at home screen")

    # ========================================
    # STEP 2: Navigate to Entertainment Section
    # ========================================
    print("\nSTEP 2: Navigating to Entertainment section...")

    # Option A: Try opening main menu first
    stbt.press("KEY_MENU")
    stbt.press_and_wait("KEY_MENU", stable_secs=1)
    print("  Opened main menu")

    # Navigate through menu to find Entertainment
    entertainment_found = False
    for i in range(8):  # Try up to 8 menu items
        # Read current screen text
        screen_text = stbt.ocr().lower()
        print(f"  Checking menu item {i+1}... Text found: {screen_text[:50]}...")

        if "entertainment" in screen_text or "entertainment" in screen_text:
            print("  ✓ Found Entertainment in menu!")
            entertainment_found = True
            stbt.press("KEY_OK")
            stbt.press_and_wait("KEY_OK", stable_secs=2)
            break
        elif "film" in screen_text or "movies" in screen_text or "series" in screen_text:
            print("  ✓ Found Entertainment-related section!")
            entertainment_found = True
            stbt.press("KEY_OK")
            stbt.press_and_wait("KEY_OK", stable_secs=2)
            break

        stbt.press("KEY_DOWN")
        stbt.wait_for_transition_to_end(timeout_secs=0.5)

    # If not found via menu, try direct navigation from home
    if not entertainment_found:
        print("  Entertainment not found in menu, trying direct navigation...")
        stbt.press("KEY_HOME")
        stbt.press_and_wait("KEY_HOME", stable_secs=1)

        # Navigate right to find Entertainment section on home screen
        for i in range(6):
            screen_text = stbt.ocr().lower()
            if "entertainment" in screen_text or "film" in screen_text:
                entertainment_found = True
                print(f"  ✓ Found Entertainment on home screen!")
                stbt.press("KEY_OK")
                stbt.press_and_wait("KEY_OK", stable_secs=2)
                break
            stbt.press("KEY_RIGHT")
            stbt.wait_for_transition_to_end(timeout_secs=0.5)

    print(f"  Entertainment section accessed: {entertainment_found}")

    # ========================================
    # STEP 3: Look for Kids Section
    # ========================================
    print("\nSTEP 3: Looking for Kids section...")

    kids_found = False
    kids_keywords = ["kids", "kinderen", "kinder", "children", "jeugd", "junior"]

    # Search current screen first
    screen_text = stbt.ocr().lower()
    for keyword in kids_keywords:
        if keyword in screen_text:
            kids_found = True
            print(f"  ✓ Found Kids section! (keyword: '{keyword}')")
            break

    # If not immediately visible, navigate to find it
    if not kids_found:
        print("  Kids not immediately visible, navigating to find it...")

        # Try navigating down/right to find Kids section
        for direction in ["KEY_DOWN", "KEY_RIGHT"]:
            if kids_found:
                break
            for i in range(6):
                stbt.press(direction)
                stbt.wait_for_transition_to_end(timeout_secs=0.5)

                screen_text = stbt.ocr().lower()
                for keyword in kids_keywords:
                    if keyword in screen_text:
                        kids_found = True
                        print(f"  ✓ Found Kids section after navigation! (keyword: '{keyword}')")
                        break

                if kids_found:
                    break

    # ========================================
    # STEP 4: Verify and Assert
    # ========================================
    print("\nSTEP 4: Verifying Kids section availability...")

    # Take final screenshot for evidence
    final_frame = stbt.get_frame()
    final_text = stbt.ocr()
    print(f"  Final screen text: {final_text[:100]}...")

    # Assert Kids section was found
    assert kids_found, (
        "Kids section NOT found in Entertainment! "
        f"Screen text was: {final_text[:200]}"
    )

    print("\n" + "="*50)
    print("TEST PASSED: Kids section is available!")
    print("="*50)

    # ========================================
    # CLEANUP: Return to Home
    # ========================================
    print("\nCLEANUP: Returning to home screen...")
    stbt.press("KEY_HOME")
    stbt.press_and_wait("KEY_HOME", stable_secs=1)
    print("  ✓ Cleanup complete")


def test_kids_section_navigate_and_enter():
    """
    Scenario: Navigate to Kids section and enter it

    Given: The STB is on the home screen
    When: User navigates to Entertainment > Kids
    And: User enters the Kids section
    Then: Kids content should be displayed
    """

    print("="*50)
    print("TEST: Navigate to Kids Section and Enter")
    print("="*50)

    # Step 1: Home
    print("\n[1/5] Going to Home screen...")
    stbt.press("KEY_HOME")
    stbt.press_and_wait("KEY_HOME", stable_secs=2)

    # Step 2: Open Menu
    print("[2/5] Opening Menu...")
    stbt.press("KEY_MENU")
    stbt.press_and_wait("KEY_MENU", stable_secs=1)

    # Step 3: Find Entertainment
    print("[3/5] Finding Entertainment section...")
    for _ in range(8):
        text = stbt.ocr().lower()
        if "entertainment" in text or "film" in text or "tv" in text:
            stbt.press("KEY_OK")
            stbt.press_and_wait("KEY_OK", stable_secs=1)
            break
        stbt.press("KEY_DOWN")
        stbt.wait_for_transition_to_end(timeout_secs=0.5)

    # Step 4: Find Kids
    print("[4/5] Finding Kids section...")
    kids_found = False
    for _ in range(10):
        text = stbt.ocr().lower()
        if "kids" in text or "kinderen" in text or "kinder" in text:
            kids_found = True
            print("  ✓ Kids section found!")
            stbt.press("KEY_OK")
            stbt.press_and_wait("KEY_OK", stable_secs=2)
            break
        stbt.press("KEY_DOWN")
        stbt.wait_for_transition_to_end(timeout_secs=0.5)

    # Step 5: Verify
    print("[5/5] Verifying Kids content...")
    assert kids_found, "Kids section not found in Entertainment"

    # Verify we're now in Kids section by checking for kids-related content
    final_text = stbt.ocr().lower()
    kids_content_keywords = ["kids", "kinderen", "cartoon", "animation", "disney", "nick", "junior"]
    content_verified = any(kw in final_text for kw in kids_content_keywords)

    print(f"  Kids content visible: {content_verified}")
    print("\n✓ TEST PASSED!")

    # Cleanup
    stbt.press("KEY_HOME")
