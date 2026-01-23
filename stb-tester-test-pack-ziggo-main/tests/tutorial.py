import stbt

from tests.ziggo.pages.apps import Apps
from tests.ziggo.pages.carousel import Carousel
from tests.ziggo.pages.guide import Guide
from tests.ziggo.pages.menu import Menu
from tests.ziggo.pages.menutest import MenuTest
from tests.ziggo.pages.playback import PlaybackBar


def test_playback_from_guide():
    Guide.launch()

def test_menu_navigation_apps():
    page = Menu.launch()
    page.navigate_to("TV APPS")
    page = Apps.launch()
    page.navigate_to("Recommended")

def test_menu_navigation_test():
    page = MenuTest.launch()
    page.navigate_to("MOVIES & SERIES")


PLAYBACK_START_TIME = stbt.prometheus.Histogram(
    "playback_start_time",
    "Histogram of time taken for Movie playback to start, in seconds",
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
             1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0,
             2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0,
             4, 5, 6, 7, 8, 9, 10])


def test_find_program_for_rent():
    page = Menu.launch()
    page.select("MOVIES & SERIES", "RENT")
    for _ in range(10):
        assert stbt.press_and_wait("KEY_DOWN")
        page = Carousel()
        if page.carousel_name == "Recently added":
            assert page.text == "More"
            assert stbt.press_and_wait("KEY_OK")
            break
    else:
        assert False, "Didn't find 'Recently added'"

    page = stbt.wait_until(Carousel)
    for _ in range(40):
        assert page, "Didn't find a Carousel page"
        if page.price:
            print(f"Found a title to rent: {page.text}")
            break
        else:
            assert stbt.press_and_wait("KEY_RIGHT")
            page = Carousel()
    else:
        assert False, "Didn't find title to rent within the first 20 titles"


def test_rent_and_playback():
    test_find_program_for_rent()

    # This navigates to "Detail page", TODO:Validate details page
    assert stbt.press_and_wait("KEY_OK")
    assert stbt.press_and_wait("KEY_OK") # This displays the pop up to enter pin
    for _ in range(4):  # Enter pin 0000
        keypress = stbt.press("KEY_0")

    playback_bar = stbt.wait_until(PlaybackBar)
    if not playback_bar:
        # No playback within 10 seconds: must be the "Continue watching" dialog.
        keypress = stbt.press("KEY_OK")
        playback_bar = stbt.wait_until(PlaybackBar)

    assert playback_bar, "Didn't find PlaybackBar within 10 seconds"
    assert stbt.wait_for_motion(mask="images/mask-spinner.png")

    # Log measurement to grafana dashboard:
    # https://ziggo.stb-tester.com/grafana/d/jxfR5Gj7k/performance-measurements?orgId=1&from=1654690721126&to=1654693424854
    latency = playback_bar._frame.time - keypress.start_time
    print(f"{playback_bar._frame.time} latency: {latency}")
    PLAYBACK_START_TIME.log(latency)
