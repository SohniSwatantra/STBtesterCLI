import time

import stbt
from tests.stbt_nursery.control_soak import soak_remote_control


def test_remote_control_reliability():
    """Presses RIGHT/LEFT 100 times (50 times each).

    Every time it checks that the keypress had the right effect by looking at
    the menu in the top of the screen, and comparing it to the previous state.
    """

    # Start from a known state
    stbt.press("KEY_BACK")
    stbt.press("KEY_BACK")
    stbt.press("KEY_BACK")
    stbt.press("KEY_MENU")
    time.sleep(1)

    soak_remote_control("KEY_RIGHT", "KEY_LEFT",
                        stbt.Region(x=0, y=0, right=1280, bottom=90))


def press_key_and_wait(key, no_of_times):
    """
    Presses a key dynamically for given number of times
    """
    for _ in range(no_of_times):
        stbt.press_and_wait(key)


def press_key(key, no_of_times):
    """
    Presses a key dynamically for given number of times
    """
    for _ in range(no_of_times):
        stbt.press(key, interpress_delay_secs=2)
