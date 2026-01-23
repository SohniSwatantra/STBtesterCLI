import random
import time
import stbt
from tests.helper import perform_video_tricks, watch_or_continue_watch_video

from tests.remote_control import press_key_and_wait

class Recordings(stbt.FrameObject):
    """TODO: Document which page this class represents.

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
    def launch() -> "Recordings":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        page = Recordings()
        if page:
            # We're already on this page, no work to do.
            return page

        # TODO: Implement navigation to get to this screen:
        assert stbt.press_and_wait("KEY_???")
        page = stbt.wait_until(Recordings)
        assert page, "Failed to launch Recordings"
        return page

    @property
    def is_visible(self) -> bool:
        # TODO: Add recordings.png to this directory. This should be an image of
        # the screen that this class is supposed to match. You can ignore
        # dynamic regions of the screen by making them transparent.
        return stbt.match("recordings.png", frame=self._frame)

    
    def do_instant_recording(self):
        """
        Record a live tv program using record button from remote
        """
        key = random.choice([*range(1,10)])
        key_to_press = f'KEY_{key}'

        stbt.press_and_wait(key_to_press)
        time.sleep(2)

        stbt.press_and_wait("KEY_RECORD")
        stbt.press_and_wait("KEY_DOWN")
        stbt.press_and_wait("KEY_OK")


    def check_recordings(self):
        """
        checks whole recording screen, tricks and deletion of recording
        """
        stbt.press_and_wait("KEY_OK")

        no_of_times = random.choice([*range(1,5)])

        press_key_and_wait("KEY_DOWN", no_of_times)
        press_key_and_wait("KEY_OK", 1)
        # watch_or_continue_watch_video()

        # perform_video_tricks()

        press_key_and_wait("KEY_BACK", 1)

        #delete the recording
        stbt.press_and_wait("KEY_RIGHT")
        press_key_and_wait("KEY_OK", 2)