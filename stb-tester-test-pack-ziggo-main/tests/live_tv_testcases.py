import time
from tests.ziggo.pages.menu.menu import Menu
from tests.ziggo.pages.moviesandseries.moviesandseries import MoviesAndSeries
import stbt
from stbt_core import Color
from tests.helper import pre_condition,ocr_text_extraction,correct_program_name,pincode_and_motion_check,create_profile_name # pylint:disable=line-too-long

LIVE_TV_POP_UP_REGION = stbt.Region(x=955, y=27, width=261, height=61)
RECORD_POP_UP_REGION = stbt.Region(x=859, y=33, width=349, height=69)
RECORDING_REGION = stbt.Region(x=61, y=293, width=1029, height=252)
RECORD_REGION = stbt.Region(x=322, y=81, width=634, height=549)
STOP_RECORDING_REGION = stbt.Region(x=549, y=397, width=185, height=33)
PROGRAM_NAME = stbt.Region(x=319, y=82, width=634, height=185)
MENU_HOME = stbt.Region(x=124, y=34, width=96, height=36)
NEXT_AVAILABLE_CHANNEL = stbt.Region(x=341, y=581, width=417, height=30)
HOME_RADIO = stbt.Region(x=56, y=679, width=88, height=28)
RADIO_PAGE = stbt.Region(x=54, y=26, width=122, height=37)
TELE_TEXT_REGION = stbt.Region(x=181, y=26, width=137, height=33)
TELETEXT_LOGO = stbt.Region(x=222, y=58, width=858, height=177)
TELETEXT_MOTION = stbt.Region(x=10, y=14, width=185, height=696)
LOGO_CHANNEL_1 = stbt.Region(x=35, y=201, width=978, height=338)
WATCHLIST_REGION = stbt.Region(x=60, y=482, width=125, height=34)
WATCHLIST_AFTER_MORE = stbt.Region(x=232, y=277, width=522, height=144)
WATCHLIST_COUNT_REGION = stbt.Region(x=116, y=94, width=66, height=37)
RENT_REGION = stbt.Region(x=50, y=559, width=549, height=38)
MOVIES_SERIES = stbt.Region(x=56, y=26, width=269, height=38)
RECENTLY_ADDED = stbt.Region(x=55, y=587, width=202, height=33)
PROVIDER_REGION = stbt.Region(x=60, y=142, width=225, height=145)
PROFILE_REGION = stbt.Region(x=535, y=31, width=220, height=58)
CREATE_PROFILE = stbt.Region(x=465, y=58, width=354, height=58)
NEW_PROFILE = stbt.Region(x=220, y=15, width=953, height=262)
MENU_REGION = stbt.Region(x=18, y=6, width=1229, height=205)
PROFILE_DELETE_REGION = stbt.Region(x=1044, y=37, width=160, height=36)
PROFILE_CREATE_REGION = stbt.Region(x=983, y=23, width=286, height=68)

def test_livetv_pause_and_playback_review_buffer():
    """
    The scripts navigates by pressing the pause key and then
    validates the pause action and afterthat by pressing the
    key fastforward to launch the live tv again
    """
    pre_condition()
    stbt.press("KEY_1")
    stbt.press("KEY_PAUSE")
    time.sleep(60)
    # stbt.wait_for_motion results in motiontimeouterror if
    # motion is not detected
    try:
        motion_result = stbt.wait_for_motion()
    except stbt.MotionTimeout:
        stbt.draw_text("The video is paused...")
        stbt.press("KEY_PAUSE")
        motion_result = stbt.wait_for_motion()
        if motion_result.motion == True:
            stbt.draw_text("playing after pause...")
            # press the key fastfoward for a match image in a specified region
            try:
                stbt.press_until_match(key="KEY_FASTFORWARD",image="images/livetv.png",max_presses=4,interval_secs=5,region=LIVE_TV_POP_UP_REGION) # pylint:disable=line-too-long
            except stbt.MatchTimeout:
                stbt.draw_text("Live tv not loaded properly")
            else:    
                stbt.draw_text("playing live tv")   
                
def test_home_radio():
    pre_condition()
    stbt.press_and_wait(key="KEY_MENU",timeout_secs=2)
    match_text_1 = stbt.match_text("HOME", region=MENU_HOME) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.draw_text("Menu has Loaded")
        for _ in range(7):
            stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
            radio_text = ocr_text_extraction(HOME_RADIO)
            if radio_text == "Radio":
                break
        stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1) 
        stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
        text_match = stbt.match_text(text="RADIO",region=RADIO_PAGE)
        if text_match.match == True:
            stbt.draw_text("Successfully reached radio")
            stbt.press("KEY_OK")
            rms_vol_result = stbt.get_rms_volume()
            stbt.draw_text(str(rms_vol_result.amplitude))
            if rms_vol_result.amplitude > 0.001:
                stbt.draw_text("Radio is playing")
            else:
                stbt.draw_text("Issue with playing radio")    
        else:
            stbt.draw_text("Issue in loading radio")
                 
                
def test_home_PIP_2215():
    pre_condition()
    stbt.press_and_wait(key="KEY_1",timeout_secs=2)
    stbt.press_and_wait(key="KEY_MENU",timeout_secs=2)
    match_text_1 = stbt.match_text("HOME", region=MENU_HOME) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.draw_text("Menu has Loaded")
        # checks for motion in the screen
        motion_result = stbt.wait_for_motion(timeout_secs=10)
        if motion_result.motion == False:
            assert "Picture in picture screen is not available for home"
        else:
            stbt.draw_text("Picture in picture screen is available for home")
    else:
        assert "Menu is not loaded properly"              
        
def test_live_tv_wrong_LCN():
    pre_condition()           
    stbt.press(key="KEY_9")
    stbt.press(key="KEY_9")
    match_text = stbt.wait_until(lambda: stbt.match(image="images/next_channel.png",region=NEXT_AVAILABLE_CHANNEL))
    if match_text.match == True:
        stbt.draw_text("Tuning to next available channel...")
    else:
        stbt.draw_text("LCN not available")
        

def test_teletext_availability():
    pre_condition()
    stbt.press_and_wait(key="KEY_1",timeout_secs=1)
    stbt.press_and_wait(key="KEY_TEXT",timeout_secs=1)
    teletext = ocr_text_extraction(TELE_TEXT_REGION)
    match_result = stbt.wait_until(lambda: stbt.match(image="images/teletext.png",region=TELETEXT_LOGO))
    if teletext == "P100" and match_result.match == True:
        stbt.draw_text("teletext is available")
    else:
        stbt.draw_text("teletext is not available")    

    
    
def test_teletext_transperancy():
    pre_condition()
    pre_condition()
    stbt.press_and_wait(key="KEY_1",timeout_secs=1)
    stbt.press_and_wait(key="KEY_TEXT",timeout_secs=1)
    teletext = ocr_text_extraction(TELE_TEXT_REGION)
    match_result = stbt.wait_until(lambda: stbt.match(image="images/teletext.png",region=TELETEXT_LOGO))
    if teletext == "P100" and match_result.match == True:
        stbt.draw_text("teletext is available")
        stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
        try:
            motion_result = stbt.wait_for_motion(region=TELETEXT_MOTION)
        except stbt.MotionTimeout:
            stbt.draw_text("Video streaming not detected")    
        else:
            if motion_result.motion == True:
                stbt.draw_text("Video straming detected")
                for _ in range(10):
                    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
                    if stbt.is_screen_black(region=TELETEXT_MOTION).black == True:
                        stbt.draw_text("teletext appeared again")
                        break
            else:
                stbt.draw_text("video streming is not detected")           
    else:
        stbt.draw_text("teletext is not available")             
        
        
def test_live_tv_record_an_episode():
    pre_condition()
    stbt.press_and_wait(key="KEY_2",timeout_secs=2)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=2)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
    record_options = ocr_text_extraction(RECORD_REGION)
    program_name = ocr_text_extraction(PROGRAM_NAME)
    program_name_corrected = correct_program_name(program_name)
    global recording_program_name
    if "Record series" or "Record this episode" in record_options:
        stbt.press_and_wait(key="KEY_DOWN",timeout_secs=2)
        stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
    else:
        stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
        stop_recording = ocr_text_extraction(STOP_RECORDING_REGION)
        if "Stop recording" in stop_recording:
            stbt.press("KEY_BACK")
        else:
            assert "stop recording is not available"    
    try:
        # checks weather the recording limit has reached or not
        stbt.wait_for_match(image="images/limit.png",timeout_secs=1)
    except stbt.MatchTimeout:    
        try:
            match_result = stbt.wait_for_match(image="images/recording_started.png",timeout_secs=3,region=RECORD_POP_UP_REGION)
        except stbt.MatchTimeout:
            stbt.draw_text("Recording started pop up not appeared properly")
        else:    
            recoding_text = ocr_text_extraction(RECORDING_REGION)
            if "Recording" in recoding_text and  match_result.match == True:
                stbt.draw_text("Recording started")
            else:
                assert "Issue with recording"    
            pre_condition()
            page = Menu.launch()
            page.navigate_to("RECORDINGS")
            stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
            stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
            match_text = stbt.match_text(text=program_name_corrected,region=stbt.Region.ALL)
            if match_text.match == True:
                stbt.draw_text("Recording has started successfully")
            else:
                assert "Issue with recording"                
    else:
        stbt.draw_text("Reached maximum recording limit....")


def test_asset_detailed_page_logo():
    pre_condition()
    stbt.press_and_wait(key="KEY_1",timeout_secs=2)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
    match_result = stbt.match(image="images/channel_1.png",region=LOGO_CHANNEL_1)
    if match_result.match == True:
        stbt.draw_text("Channel logo is available")
    else:
        stbt.draw_text("Channel logo is not available")          
        
def test_vod_purchase():
    pre_condition()
    page = MoviesAndSeries.launch()
    page.navigate_to("RENT") 
    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
    for _ in range(10):
        stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
        recently_added = ocr_text_extraction(RECENTLY_ADDED)
        if "Recently added" in recently_added:
            stbt.press_and_wait(key="KEY_DOWN",timeout_secs=2)
            stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
            break
    stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
    rent = ocr_text_extraction(RENT_REGION)
    if "RENT" not in rent:
        stbt.press_and_wait(key="KEY_BACK",timeout_secs=1)
        for _ in range(10):
            stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=2)
            stbt.press_and_wait(key="KEY_OK")
            rent = ocr_text_extraction(RENT_REGION)
            if "RENT" in rent:
                break
            else:
                stbt.press_and_wait(key="KEY_BACK",timeout_secs=1)
                continue
        stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
        pincode_and_motion_check()
    else:
        stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
        pincode_and_motion_check()
        
def test_VOD_providers():
    pre_condition()
    page = MoviesAndSeries.launch()
    page.navigate_to("PROVIDERS") 
    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
    if stbt.is_screen_black(region=PROVIDER_REGION).black == False:
        stbt.draw_text("Provider present")
    else:
        stbt.draw_text("Provider not present") 
 

def test_create_delete_profile():
    pre_condition()
    stbt.press_and_wait(key="KEY_MENU",timeout_secs=2)
    match_text_1 = stbt.match_text("HOME", region=MENU_HOME) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.draw_text("Menu has Loaded")
        for _ in range(6):
            stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
        stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
        match_text_2 = stbt.match_text("Profiles", region=PROFILE_REGION) # pylint:disable=line-too-long
        if match_text_2.match == True:
            stbt.draw_text("Profiles Loaded")
            stbt.press_until_match(key="KEY_RIGHT",image="images/new_profile.png",max_presses=10)
            stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
            match_text_3 = stbt.match_text("Create a profile", region=CREATE_PROFILE) # pylint:disable=line-too-long
            if match_text_3.match == True:
                stbt.draw_text("create a profile Loaded")
                stbt.press_and_wait(key="KEY_DOWN",timeout_secs=2)
                create_profile_name()
                match_result = stbt.wait_until(lambda: stbt.match(image="images/create_profile.png",region=CREATE_PROFILE))
                if match_result.match == True:
                    stbt.draw_text("profile created successfully")
                    for _ in range(6):
                        stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
                        stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
                        match_text_2 = stbt.match_text("Profiles", region=PROFILE_REGION) # pylint:disable=line-too-long
                        if match_text_2.match == True:
                            stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
                            stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
                            stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
                            stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
                            stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
                            stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
                            stbt.press_and_wait(key="KEY_UP",timeout_secs=1)
                            stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
                            match_result = stbt.wait_until(lambda: stbt.match(image="images/delete_profile.png",region=PROFILE_DELETE_REGION))
                            if match_result.match == True:
                                stbt.draw_text("profile deleted successfully")
                            else:
                                stbt.draw_text("Issue with profile deletion")
                else:
                    stbt.draw_text("issue with profile creation")      
            else:
                stbt.draw_text("create profile not loaded properly")        
        else:
            stbt.draw_text("profiles not loaded properly")               
    else:
        stbt.draw_text("Menu not loaded")                

def test_personal_home_posters():
    pre_condition()
    stbt.press_and_wait(key="KEY_MENU",timeout_secs=2)
    match_text_1 = stbt.match_text("HOME", region=MENU_HOME) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.draw_text("Menu has Loaded")
        for _ in range(7):
            stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
            watchlist_text = ocr_text_extraction(WATCHLIST_REGION)
            if watchlist_text == "Watchlist":
                break
        stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
        black_result = stbt.is_screen_black(region=WATCHLIST_AFTER_MORE)
        if black_result.black == False:
            stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
            watchlist_count = ocr_text_extraction(WATCHLIST_COUNT_REGION)
            stbt.draw_text(watchlist_count)
            

    
