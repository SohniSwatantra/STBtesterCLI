"""
Test Movie Playback
Tests that a user can navigate to Movies & Series and play a movie.
"""
import stbt_core as stbt


def test_movie_playback():
    """
    Scenario: Play a movie from Movies & Series section

    Given: The STB is on the home screen
    When: User navigates to Movies & Series
    And: User selects a movie
    And: User starts playback
    Then: Video playback should start (motion detected)
    """
    # Step 1: Go to Home screen
    stbt.press("KEY_HOME")
    stbt.press_and_wait("KEY_HOME", stable_secs=2)

    # Step 2: Navigate to Movies & Series
    # From home, navigate right to find Movies & Series section
    for _ in range(5):
        stbt.press("KEY_RIGHT")
        stbt.wait_for_transition_to_end(timeout_secs=1)

    # Press down to enter the content row
    stbt.press("KEY_DOWN")
    stbt.press_and_wait("KEY_DOWN", stable_secs=1)

    # Step 3: Select a movie (first available)
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=2)

    # Step 4: Start playback
    # On movie detail page, press OK or PLAY to start
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=3)

    # Step 5: Verify video is playing using motion detection
    # Wait for motion which indicates video playback
    motion_detected = stbt.wait_for_motion(
        timeout_secs=10,
        consecutive_frames=5
    )

    assert motion_detected, "Video playback not detected - no motion found"

    # Additional verification: ensure motion continues for a few seconds
    stbt.wait_for_motion(timeout_secs=5, consecutive_frames=10)

    # Cleanup: Stop playback and return to home
    stbt.press("KEY_STOP")
    stbt.press("KEY_HOME")


def test_movie_playback_from_search():
    """
    Scenario: Search for a movie and play it

    Given: The STB is on the home screen
    When: User opens search
    And: User searches for a movie
    And: User selects and plays the movie
    Then: Video playback should start
    """
    # Go to Home
    stbt.press("KEY_HOME")
    stbt.press_and_wait("KEY_HOME", stable_secs=2)

    # Open search (usually accessible via a dedicated button or menu)
    stbt.press("KEY_MENU")
    stbt.press_and_wait("KEY_MENU", stable_secs=1)

    # Navigate to search option
    for _ in range(3):
        stbt.press("KEY_DOWN")
        stbt.wait_for_transition_to_end(timeout_secs=0.5)

    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=2)

    # Select first search result
    stbt.press("KEY_DOWN")
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=2)

    # Play the content
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=3)

    # Verify playback
    motion_detected = stbt.wait_for_motion(timeout_secs=10)
    assert motion_detected, "Video playback not detected"

    # Cleanup
    stbt.press("KEY_STOP")
    stbt.press("KEY_HOME")


def test_movie_playback_vod():
    """
    Scenario: Play a VOD movie

    Given: The STB is on the home screen
    When: User navigates to VOD/On Demand section
    And: User browses and selects a free movie
    And: User starts playback
    Then: Video should play with motion detected
    """
    # Go to Home
    stbt.press("KEY_HOME")
    stbt.press_and_wait("KEY_HOME", stable_secs=2)

    # Navigate to VOD section (typically in main menu)
    stbt.press("KEY_MENU")
    stbt.press_and_wait("KEY_MENU", stable_secs=1)

    # Look for On Demand / VOD option
    for _ in range(5):
        # Read current menu item
        text = stbt.ocr()
        if "demand" in text.lower() or "vod" in text.lower() or "film" in text.lower():
            break
        stbt.press("KEY_DOWN")
        stbt.wait_for_transition_to_end(timeout_secs=0.5)

    # Select VOD
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=2)

    # Select first category
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=1)

    # Select first movie
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=2)

    # Start playback (might need to select "Play" button on detail page)
    stbt.press("KEY_OK")
    stbt.press_and_wait("KEY_OK", stable_secs=3)

    # Verify video playback
    try:
        stbt.wait_for_motion(timeout_secs=15, consecutive_frames=5)
    except stbt.MotionTimeout:
        # If no motion, might need to press play again
        stbt.press("KEY_PLAY")
        stbt.wait_for_motion(timeout_secs=10, consecutive_frames=5)

    # Cleanup
    stbt.press("KEY_STOP")
    stbt.press("KEY_HOME")
