"""Feature: TV-Guide.

    This file contains test scripts that validates TV-Guide features.

    Check points covered:

    1. Info availability

    2. Picture-in-picture

    3. 7 days program availability

    4. 14 days program availability

    5. Forward/Backward

    6. Synopsis

    7. Sort by Genre

    8. Replay availability

    """

import stbt
from tests.helper import pre_condition, extract_text
from tests.helper import extract_number_from_date
from tests.helper import ocr_text_extraction, text_search, check_days

DATE_FILTER_REGION = stbt.Region(x=112, y=89, right=286, bottom=134)
DATE_FILTER_SEVEN_DAYS = stbt.Region(x=673, y=75, right=734, bottom=101)
DATE_FILTER_FOURTEEN_DAYS = stbt.Region(x=693, y=577, right=752, bottom=606)
GUIDE_SERIES_RECORDING = stbt.Region(x=153, y=586, right=472, bottom=614)
GUIDE_INFO_REGION = stbt.Region(x=154, y=619, right=907, bottom=669)
GUIDE_TV_REPLAY = stbt.Region(x=34, y=16, right=384, bottom=73)
GUIDE_REPLAY_ICON = stbt.Region(x=163, y=593, width=26, height=26)
GUIDE_NEWS_REGION = stbt.Region(x=682, y=540, right=748, bottom=572)
GUIDE_GENRE_REGION = stbt.Region(x=260, y=94, right=439, bottom=132)

def test_check_info_availability_guide():
    """
    The script navigates to Guide and checks for program information availabilty
    """
    # pre condition
    pre_condition()
    # tune to Guide
    stbt.press_and_wait("KEY_GUIDE")
    # checking for TV GUIDE & REPLAY text for validating guide
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.draw_text("Guide Loaded")
        match_text_2 = stbt.match_text("No Info", region=stbt.Region.ALL)
        if match_text_2.match == True:
            assert "Program information not loaded properly"
        else:
            stbt.draw_text("Program information loaded properly")
    else:
        assert "Guide is not loaded properly"


def test_PIP_check_guide():
    """
    The script navigates to Guide and check
    for pipcture in picture screen availability
    """
    # pre condition
    pre_condition()
    # tune to guide
    stbt.press_and_wait("KEY_GUIDE")
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.draw_text("Guide Loaded")
        # checks for motion in the screen
        motion_result = stbt.wait_for_motion(timeout_secs=10)
        if motion_result.motion == False:
            assert "Picture in picture screen is not available"
        else:
            stbt.draw_text("Picture in picture screen available")
    else:
        assert "Guide is not loaded properly"

def test_seven_days_availability_guide():
    """
    The script navigates to guide and selects today
    and scroll up to the last day which is the
    past 7th day.The selected text is compared with
    today and validated.After tuning to channel 1
    checks whether the date loaded at the bottom
    portion matches with the top date text
    """
    global upper_date # pylint:disable=global-variable-undefined
    pre_condition()
    stbt.press_and_wait("KEY_GUIDE")
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match== True:
        stbt.draw_text("Guide Loaded")
        stbt.press_and_wait("KEY_1")
        stbt.press_and_wait("KEY_UP")
        stbt.press_and_wait("KEY_OK")
        # loop untill the desired region is not black
        for _ in range(8):
            stbt.press_and_wait("KEY_UP")
            if stbt.is_screen_black(region=DATE_FILTER_SEVEN_DAYS).black == False: # pylint:disable=line-too-long
                stbt.press_and_wait("KEY_OK")
                break
        date_text_upper = ocr_text_extraction(DATE_FILTER_REGION)
        stbt.draw_text(date_text_upper)
        no_days = check_days(7)
        # handling special cases of ocr extraction
        if "?" in date_text_upper:
            upper_date = 7
        elif "Z" in date_text_upper:
            upper_date = 2
        else:
            upper_date = extract_number_from_date(date_text_upper)
        stbt.draw_text(str(upper_date))
        if no_days == upper_date:
            stbt.draw_text("past 7 days are available")
        else:
            assert "Past 7 days are not available"
        stbt.press_and_wait("KEY_1")
        date_text_lower = ocr_text_extraction(GUIDE_SERIES_RECORDING)
        stbt.draw_text(date_text_lower)
        lower_date = extract_number_from_date(date_text_lower)
        if upper_date != lower_date:
            assert "Date is not selected properly for past 7 days"
        else:
            stbt.draw_text("Dates are loaded properly for past 7 days")
    else:
        assert "Guide is not loaded properly"

def test_fourteen_days_availability_guide():
    """
    The script navigates to guide and selects
    today and scroll down to the last day which is the
    future 14th day.The selected text is compared with
    today and validated.After tuning to channel 1
    checks whether the date loaded at the bottom portion
    matches with the top date text
    """
    global date_upper # pylint:disable=global-variable-undefined
    pre_condition()
    stbt.press_and_wait("KEY_GUIDE")
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.draw_text("Guide loaded")
        stbt.press_and_wait("KEY_1")
        stbt.press_and_wait("KEY_UP")
        stbt.press_and_wait("KEY_OK")
        # loop untill the desired region is not black
        for _ in range(15):
            stbt.press_and_wait("KEY_DOWN")
            if stbt.is_screen_black(region=DATE_FILTER_FOURTEEN_DAYS).black == False: # pylint:disable=line-too-long
                stbt.press_and_wait("KEY_OK")
                break
        date_text_upper = ocr_text_extraction(DATE_FILTER_REGION)
        stbt.draw_text(date_text_upper)
        no_of_days = check_days(13)
        # handling special cases of ocr extraction
        if "?" in date_text_upper:
            date_upper = 7
        elif "Z" in date_text_upper:
            date_upper = 2
        else:
            date_upper = extract_number_from_date(date_text_upper)
        if no_of_days == date_upper:
            stbt.draw_text("future 14 days are available")
        else:
            assert "future 14 days are not available"
        stbt.press_and_wait("KEY_1")
        date_text_lower = ocr_text_extraction(GUIDE_SERIES_RECORDING)
        stbt.draw_text(date_text_lower)
        date_lower = extract_number_from_date(date_text_lower)
        if date_upper != date_lower:
            assert "Date is not selected properly for future 14 days"
        else:
            stbt.draw_text("Dates are loaded properly for future 14 days")
    else:
        assert "Guide is not loaded properly"

def test_forward_backward_check_guide():
    """
    The script navigates to guide and tune to channel 1
    and using fast forward and rewind keys selections were made.
    Validations are done by text extraction and comparison
    """
    pre_condition()
    stbt.press_and_wait("KEY_GUIDE")
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.press_and_wait("KEY_1")
        today_text_1 = ocr_text_extraction(DATE_FILTER_REGION)
        stbt.draw_text(today_text_1)
        stbt.press_and_wait("KEY_FASTFORWARD")
        tomorrow_text = ocr_text_extraction(DATE_FILTER_REGION)
        stbt.draw_text(tomorrow_text)
        stbt.press_and_wait("KEY_REWIND")
        today_text_2 = ocr_text_extraction(DATE_FILTER_REGION)
        stbt.draw_text(today_text_2)
        stbt.press_and_wait("KEY_REWIND")
        yesterday_text = ocr_text_extraction(DATE_FILTER_REGION)
        stbt.draw_text(yesterday_text)
        if "Tomorrow" in tomorrow_text:
            stbt.draw_text("fast forward executed properly")
        else:
            assert "Some issue with fast forward"
        if "Today" in today_text_2 and "Yesterday" in yesterday_text:
            stbt.draw_text("Rewind executed properly")
        else:
            assert "Some issue with rewind"
    else:
        assert "Guide is not loaded properly"

def test_synopsis_guide():
    """
    The script navigates to guide and tune to channel 1
    and in the bottom region searches for text
    """
    pre_condition()
    stbt.press_and_wait("KEY_GUIDE")
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.press_and_wait("KEY_1")
        info_text = ocr_text_extraction(GUIDE_INFO_REGION)
        stbt.draw_text(info_text)
        info_bool = text_search(info_text)
        if info_bool == True:
            stbt.draw_text("Synopsis available")
        else:
            assert "Synopsis not available"
    else:
        assert "Guide is not loaded properly"

def test_sort_by_genre_guide():
    """The scrpt navigates to guide and go to ALL CHANNELS option.
    In that option navigates down unitill News region is reached.
    Extracts the text in the top portion and by using down key
    checks wheather the news programs are loaded correctly
    """
    pre_condition()
    stbt.press_and_wait("KEY_GUIDE")
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.press_and_wait("KEY_1")
        stbt.press_and_wait("KEY_UP")
        stbt.press_and_wait("KEY_RIGHT")
        stbt.press_and_wait("KEY_OK")
        for _ in range(12):
            stbt.press_and_wait("KEY_DOWN")
            if stbt.is_screen_black(region=GUIDE_NEWS_REGION).black == False:
                stbt.press_and_wait("KEY_OK")
                news_text = ocr_text_extraction(GUIDE_GENRE_REGION)
                stbt.draw_text("Successfully selected news in the all channel filter section") # pylint:disable=line-too-long
                break
        corrected_news_text = extract_text(news_text)
        stbt.draw_text(corrected_news_text)
        stbt.press_and_wait("KEY_DOWN")
        bottom_text_1 = ocr_text_extraction(GUIDE_SERIES_RECORDING)
        stbt.draw_text(bottom_text_1)
        stbt.press_and_wait("KEY_DOWN")
        bottom_text_2 = ocr_text_extraction(GUIDE_SERIES_RECORDING)
        stbt.draw_text(bottom_text_2)
        if ((corrected_news_text in bottom_text_1) or (corrected_news_text in bottom_text_2)): # pylint:disable=line-too-long
            stbt.draw_text("News programs are successfully loaded")
        else:
            assert "News programs are not sorted properly"
    else:
        assert "Guide is not loaded properly"

def test_replay_availability_guide():
    """
    The script navigates to guide and tune to channel and go
    to a past program by pressing lefy key.The script checks
    for the replay icon in the video frame for both channel 1 and channel 6.
    """
    pre_condition()
    stbt.press_and_wait("KEY_GUIDE")
    match_text_1 = stbt.match_text("TV GUIDE & REPLAY", region=GUIDE_TV_REPLAY) # pylint:disable=line-too-long
    if match_text_1.match == True:
        stbt.press_and_wait("KEY_1")
        stbt.press_and_wait("KEY_LEFT")
        image = stbt.load_image("images/replay_icon.png")
        match_replay_bool = stbt.match(image=image, region=GUIDE_REPLAY_ICON)
        if match_replay_bool.match == True:
            stbt.draw_text("Replay is available for channel 1")
        else:
            assert "Replay is not available for channel 1"
        stbt.press_and_wait("KEY_6")
        stbt.press_and_wait("KEY_LEFT")
        match_replay_bool = stbt.match(image=image, region=GUIDE_REPLAY_ICON)
        if match_replay_bool.match == True:
            stbt.draw_text("Replay is available for channel 6")
        else:
            assert "Replay is not available for channel 6"
