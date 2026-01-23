import random
import time
import re
import datetime
import stbt
from stbt import OcrEngine, OcrMode
from tests.remote_control import press_key, press_key_and_wait
from tests.ziggo.pages.button.button import Button

PINCODE_POPUP = stbt.Region(x=353, y=349, width=572, height=74)


def pre_condition():
    stbt.press("KEY_BACK")
    stbt.press("KEY_BACK")
    stbt.press("KEY_BACK")
    stbt.press("KEY_BACK")
    
#def navigate_to_target(target):

    
def orange_underline():
    regions = stbt.find_regions_by_color(frame=None,
            color=(16, 135, 225))
    if len(regions) == 1:
        return regions[0]
    else:
        return None
    
def correct_program_name(program_name):
    corrected = ' '.join(program_name.split()[:1]) 
    return corrected   

# if we input a string with date to this function
# it will return the corresponding day

def extract_number_from_date(date):
    number = re.search(r'\d+', date)
    date_extracted = int(number.group())
    return date_extracted

# search words

def extract_text(text):
    text_extracted = re.search(r'\w+', text)
    genre = str(text_extracted.group())
    return genre

def extract_program_name(text):
    list_name = text.split(" @ ")
    name = list_name[1]
    return name

# return true if text found

def text_search(text):
    searched = re.search(r'\w+', text)
    if searched:
        return True
    else:
        return False


# checks whether the number is 7 or 13 and if it is 7 adds it to
# todays's date and return corresponding date
# if it is 13 calculates the difference between
# todays date and datetime object for 13 days
# difference and returns corresponding difference

def check_days(number):
    if number == 13:
        date = datetime.datetime.today() + datetime.timedelta(days=number)
    elif number == 7:
        date = datetime.datetime.today() - datetime.timedelta(days=number)
    return date.day

# take region and produce output as the oct extracted text

def ocr_text_extraction(ocr_region):
    date_text = stbt.ocr(region=ocr_region,
                         engine=OcrEngine.TESSERACT,
                         mode=OcrMode.PAGE_SEGMENTATION_WITHOUT_OSD,
                         tesseract_config={}, tesseract_user_patterns=r'\n',
                         tesseract_user_words=None,
                         text_color=None, text_color_threshold=25,
                         upsample=True)
    return date_text


def pincode_and_motion_check():
    pincode_popup = ocr_text_extraction(PINCODE_POPUP)
    if "Please confirm your purchase" in pincode_popup:
        stbt.press("KEY_0")
        stbt.press("KEY_0")
        stbt.press("KEY_0")
        stbt.press("KEY_0")
        motion_result = stbt.wait_for_motion(timeout_secs=10)
        if motion_result.motion == True:
            stbt.draw_text("Purchased video is playing")
        else:
            stbt.draw_text("Issue with purchased video")

def create_profile_name():
    stbt.press_and_wait(key="KEY_UP",timeout_secs=1)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
    stbt.press_and_wait(key="KEY_LEFT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_LEFT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
    stbt.press_and_wait(key="KEY_LEFT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_UP",timeout_secs=1)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_RIGHT",timeout_secs=1)
    stbt.press_and_wait(key="KEY_DOWN",timeout_secs=1)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=1)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
    stbt.press_and_wait(key="KEY_DOWN",timeout_secs=2)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=2)
    stbt.press_and_wait(key="KEY_DOWN",timeout_secs=2)
    stbt.press_and_wait(key="KEY_DOWN",timeout_secs=2)
    stbt.press_and_wait(key="KEY_DOWN",timeout_secs=2)
    stbt.press_and_wait(key="KEY_OK",timeout_secs=2)


def watch_or_continue_watch_video():
    """
    checks for video playback and if not presses continue or live watch
    """
    try:
        stbt.wait_for_motion()
    except stbt.MotionTimeout:
        # No playback within 10 seconds: must be the "Continue watching" dialog.
        stbt.press("KEY_OK")


def record_a_content():
    """
    Records a content
    """
    # is_record_button=stbt.match("record_button.png", frame=self._frame)
    is_record_button = True
    if is_record_button:
        stbt.press("KEY_OK")
        stbt.press("KEY_OK")


def perform_video_tricks():
    # forward the video at normal speed
    stbt.press_and_wait("KEY_FASTFORWARD")
    stbt.press("KEY_OK")

    time.sleep(2)

    # forward the video at 2x speed
    press_key("KEY_FASTFORWARD", 2)
    stbt.press("KEY_OK")
    time.sleep(2)

    # forward the video at 3x speed
    press_key("KEY_FASTFORWARD", 3)
    stbt.press("KEY_OK")
    time.sleep(2)

    # rewind the video at normal speed
    stbt.press_and_wait("KEY_REWIND")
    stbt.press("KEY_OK")
    time.sleep(2)

    # rewind the video at 2x speed
    press_key("KEY_REWIND", 2)
    stbt.press("KEY_OK")
    time.sleep(2)

    # rewind the video at 3x speed
    press_key("KEY_REWIND", 3)
    stbt.press("KEY_OK")
    time.sleep(2)

    stbt.press("KEY_OK", interpress_delay_secs=2)

    # pause the video
    stbt.press("KEY_PAUSE", interpress_delay_secs=3)


def check_tele_text():
    """
    starts the tele text for a live channel and checks for transperancy
    """
    # random channel number
    key = random.choice([*range(1, 10)])
    key_to_press = f'KEY_{key}'

    stbt.press_and_wait(key_to_press)
    stbt.press_and_wait("KEY_TEXT")
    time.sleep(4)

    press_key_and_wait("KEY_OK", 4)

    stbt.press('KEY_BACK')


def back_to_top(section='Discover', is_vod=False, is_watchlist=False):
    """
    checks for the Back To Top functionality,
    moves to the end of the screen for back to top button
    """
    stbt.press("KEY_DOWN")
    button = Button()
    number = 5 if section == 'Providers' else 10
    number = 15 if is_vod else number
    number = 6 if is_watchlist else number
    for _ in range(number):
        if button.is_visible and button.text == "Back to top":
            break
        stbt.press("KEY_DOWN", interpress_delay_secs=2)
    # Back To Top button
    stbt.press_and_wait("KEY_OK")


def enter_pin(key): 
    """
    Function to enter parental pin
    """
    for _ in range(4):
        stbt.press(key, interpress_delay_secs=2)


def check_A_rated_channels():
    """
    tune to adult channel, and try wrong and correct pin
    """
    key = random.choice([*range(1, 4)])
    key_to_press = f'KEY_{key}'
    stbt.press('KEY_7')
    stbt.press('KEY_9')
    stbt.press(key_to_press)

    # check for wrong pin
    time.sleep(2)
    stbt.press_and_wait("KEY_OK")
    enter_pin("KEY_1")
    time.sleep(2)
    press_key('KEY_BACK', 4)


def check_history_channel():
    """
    Tunes to history channel number 28
    """
    stbt.press("KEY_2")
    stbt.press("KEY_8")

    time.sleep(4)
