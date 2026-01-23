import imp
import time
import stbt
from tests.helper import perform_video_tricks, record_a_content, watch_or_continue_watch_video
from tests.remote_control import press_key_and_wait

DATE_FILTER_REGION = stbt.Region(x=466, y=4, width=349, height=713)
CONTENT_REGION = stbt.Region(x=44, y=19, width=1230, height=514)

class Guide(stbt.FrameObject):
    """The Programme Guide.

    This is a "Page Object" that represents a particular page of your
    app. Each instance of this class has a member (``self._frame``)
    which is a video-frame captured when the instance is created.   
    Properties of this class describe the state of the device-under-test
    *when the instance was created*, so properties must pass
    ``frame=self._frame`` to any image-processing functions (such as
    `stbt.match` or `stbt.ocr`).

    For more information about Page Objects, see "Object Repository" in
    the Stb-tester manual:
    https://stb-tester.com/manual/object-repository

    You can debug your Page Objects in the Object Repository tab of
    your Stb-tester Portal:
    https://ziggo.stb-tester.com/app/#/objects
    """

    @staticmethod
    def launch() -> "Guide":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        page = Guide()
        if page:
            # We're already on this page, no work to do.
            return page

        # stbt.press("KEY_BACK")
        # stbt.press("KEY_BACK")
        # stbt.press("KEY_BACK")
        # stbt.press("KEY_1")
        stbt.press("KEY_GUIDE")
        page = stbt.wait_until(Guide)
        assert page, "Failed to launch Guide"
        return page
    
    # def match_replay(self, replay_image, regions):
    #       match_replay = stbt.match(image=replay_image, frame=self._frame, region=regions)
    #       if match_replay: 
    #         return True
    #       else:
    #           return False  

    @property
    def is_visible(self) -> bool:
        return stbt.match("guide.png", frame=self._frame)

    @property
    def selected_title(self) -> str:
        """The title of the selected program."""
        return stbt.ocr(region=stbt.Region(x=155, y=553, width=776, height=34),
                        frame=self._frame)
          

    def scroll_to_days(self, no_of_days):
        """
        function scrolls through Date filter, to +7, -7 and today
        """
        remote_key = "KEY_DOWN" if no_of_days == 21 else "KEY_UP"
        for day in range(no_of_days):
            stbt.press_and_wait(remote_key, region=DATE_FILTER_REGION)
        stbt.press_and_wait("KEY_OK")


    def check_date_filter(self):
        """
        Navigates to the date filter in TV Guide
        and checks for +7 and -7 days content
        """
        time.sleep(2)
        stbt.press("KEY_1")
        stbt.press_and_wait("KEY_UP", region=DATE_FILTER_REGION)
        stbt.press_and_wait("KEY_OK", region=DATE_FILTER_REGION)

        #scroll up back to 7th day
        self.scroll_to_days(7)

        #content for 7th day from today is shown

        #scroll to 14th day
        stbt.press_and_wait("KEY_OK", region=DATE_FILTER_REGION)
        self.scroll_to_days(21)

        #content for 14th day is shown

        #scroll back to today
        stbt.press_and_wait("KEY_OK", region=DATE_FILTER_REGION)
        self.scroll_to_days(13)


    def check_content_for_TV_Guide(self):
        """
        checks the content of TV Guide,
        for previous and upcoming dates
        and the channels
        """
        #moving cursor to content
        stbt.press_and_wait("KEY_DOWN")
        #check for Replay content for previous date
        press_key_and_wait("KEY_REWIND", 2)
        # press_key_and_wait("KEY_OK", 2)
        # watch_or_continue_watch_video()
        # wait for 10 seconds
        time.sleep(2)
        # press_key_and_wait("KEY_BACK", 2)

        #Check for recording a content
        press_key_and_wait("KEY_FASTFORWARD", 4)
        stbt.press_and_wait("KEY_OK")
        record_a_content()
        time.sleep(4)
        stbt.press_and_wait("KEY_BACK")

        #Move back to today
        press_key_and_wait("KEY_REWIND", 2)

        #check for other channels
        press_key_and_wait("KEY_CHANNELDOWN", 3)
        # press_key_and_wait("KEY_OK", 2)
        # watch_or_continue_watch_video()
        # wait for 5 seconds
        time.sleep(2)
        # press_key_and_wait("KEY_BACK", 2)   

        press_key_and_wait("KEY_CHANNELUP", 3)
        # press_key_and_wait("KEY_OK", 2)
        # watch_or_continue_watch_video()
        # wait for 10 seconds
        time.sleep(2)
        # press_key_and_wait("KEY_BACK", 2)

        #check for Replay content on same day
        press_key_and_wait("KEY_LEFT", 2)
        # press_key_and_wait("KEY_OK", 2)
        # watch_or_continue_watch_video()
        # wait for 10 seconds
        time.sleep(2)
        # press_key_and_wait("KEY_BACK", 2)

    
    def check_replay_section(self):
        """
        Verifies Replay section along with Play/Pause,
        playing asset at normal speed, Tricks mode and slow motion

        note: expecting control to be present at TV Guide & Replay screen
        """
        # for replay content move to back date
        press_key_and_wait("KEY_REWIND", 2)
        press_key_and_wait("KEY_OK", 2)

        watch_or_continue_watch_video()
        perform_video_tricks()
        