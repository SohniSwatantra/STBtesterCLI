import time
import random
import stbt

from tests.eos_sanity_SoftwareCheck import test_eos_sanity_softwareversion
from tests.remote_control import press_key, press_key_and_wait
from tests.ziggo.pages.apps.apps import Apps
from tests.ziggo.pages.guide.guide import Guide

from tests.ziggo.pages.menu.menu import Menu
from tests.ziggo.pages.moviesandseries.moviesandseries import MoviesAndSeries
from tests.ziggo.pages.profile.profile import Profile
from tests.ziggo.pages.recordings.recordings import Recordings
from tests import helper
from tests.ziggo.pages.settings.settings import Settings



def test_eos_sanity_5654():
    EOS_SANITY_MENU_LAUNCH_TIME = stbt.prometheus.Histogram(
    "eos_sanity_menu_launch_time_seconds",
    "Time to launch the menu.",
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 60])


    EOS_SANITY_DURATION = stbt.prometheus.Gauge(
    "eos_sanity_duration_seconds",
    "Duration of test_eos_sanity.")

    """
    The script navigates to the whole EOS box and checks the flow
    """
    test_eos_sanity_softwareversion()

    start_time = time.time()

    # pre condition, tune to channel 1 and perform
    stbt.press_and_wait("KEY_1")

    # starting with the Home
    stbt.draw_text("launching and navigating through home", 13)
    menu = Menu()
    menu_launch_start_time = time.time()
    menu.launch()
    EOS_SANITY_MENU_LAUNCH_TIME.log(time.time() - menu_launch_start_time)

    # menu.select("HOME")
    helper.back_to_top()

    # check A-Rated channels
    stbt.draw_text("checking for rated channel", 22)
    helper.check_A_rated_channels()

    # check history channel
    stbt.draw_text("checking for history channel", 5)
    helper.check_history_channel()

    # Check the TV Guide Section
    stbt.draw_text("opening TV guide", 10)
    menu.launch()
    press_key_and_wait("KEY_RIGHT", 1)
    stbt.press("KEY_OK")
    guide = Guide()
    stbt.draw_text("filtering based on date", 79)
    guide.check_date_filter()
    time.sleep(3)
    stbt.draw_text("checking content in TV guide", 81)
    guide.check_content_for_TV_Guide()

    # Check Replay section
    stbt.draw_text("replay and trick play", 87)
    guide.check_replay_section()
    # Check Zapping
    # menu.launch()
    stbt.draw_text("zapping", 70)
    menu.perform_zapping()

    # Check Tele Text
    stbt.draw_text("checking for teletext", 56)
    helper.check_tele_text()

    # Check VOD
    stbt.draw_text("checking each section under discover", 64)
    menu.launch()
    press_key_and_wait("KEY_RIGHT", 3) 
    time.sleep(3)
    stbt.press_and_wait('KEY_OK')
    movies_and_series = MoviesAndSeries()
    helper.back_to_top()
    stbt.draw_text("checking genre & other sections under movies,series,kids&rent", 326) # pylint:disable=line-too-long
    movies_and_series.play_vod()
    rec = Recordings()
    #Do recording of live channel
    stbt.draw_text("instant recording", 40)
    rec.do_instant_recording()

    # Check Recordings Tab
    stbt.draw_text("checking for recordings & deleting series recording", 68)
    menu.launch()
    press_key_and_wait("KEY_RIGHT", 4)
    stbt.press_and_wait('KEY_OK')
    # menu.select("RECORDINGS")
    rec.check_recordings()

    # Check Profiles
    stbt.draw_text("creating and deleting profile", 79)
    menu.launch()
    press_key("KEY_LEFT", 2)
    stbt.press("KEY_OK")
    profile = Profile()
    profile.check_profile()
    profile.delete_profile()

    # Check Settings
    stbt.draw_text("checking each section in settings", 35)
    menu.launch()
    press_key("KEY_LEFT", 3)
    stbt.press("KEY_OK")
    settings = Settings()
    settings.check_settings()
    stbt.draw_text("checking for locked channel", 60)
    settings.check_parental_control()
    settings.postcheck()
    # check Watchlist
    stbt.draw_text("adding assset to watchlist", 38)
    menu.launch()
    press_key("KEY_RIGHT", 3)
    time.sleep(2)
    stbt.press("KEY_OK")
    time.sleep(3)
    press_key("KEY_DOWN", 3)
    press_key("KEY_RIGHT", random.randint(1, 8))
    stbt.press("KEY_OK")
    movies_and_series = MoviesAndSeries()
    movies_and_series.add_to_watchlist()
    menu.launch()
    stbt.draw_text("checking asset under watchlist", 19)
    menu.navigate_to_watchlist()

    # app navigation
    stbt.draw_text("lanching an app from appstore", 48)
    menu.launch()
    press_key_and_wait("KEY_RIGHT", 2)
    stbt.press("KEY_OK")
    time.sleep(2)
    apps = Apps()
    apps.navigate_appstore()
    press_key("KEY_MENU", 8)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Total script duration: {duration}")
    EOS_SANITY_DURATION.set(duration)
