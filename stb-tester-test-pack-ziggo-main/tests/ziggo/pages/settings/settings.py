import time
import stbt
from tests.helper import enter_pin

from tests.remote_control import press_key


class Settings(stbt.FrameObject):
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
    def launch() -> "Settings":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        page = Settings()
        if page:
            # We're already on this page, no work to do.
            return page

        # TODO: Implement navigation to get to this screen:
        assert stbt.press_and_wait("KEY_???")
        page = stbt.wait_until(Settings)
        assert page, "Failed to launch Settings"
        return page

    @property
    def is_visible(self) -> bool:
        # TODO: Add settings.png to this directory. This should be an image of
        # the screen that this class is supposed to match. You can ignore
        # dynamic regions of the screen by making them transparent.
        return stbt.match("settings.png", frame=self._frame)

    def check_settings(self):
        """
        Navigate through the settings menu 
        """
        stbt.press("KEY_UP")
        for _ in range(7):
            stbt.press_and_wait("KEY_RIGHT")
            time.sleep(3)

    def check_parental_control(self):
        press_key("KEY_RIGHT",2)
        time.sleep(2)

        #move to lock channels
        press_key("KEY_DOWN",4)
        time.sleep(3)
        stbt.press("KEY_OK")

        #enter pin
        enter_pin('KEY_0')
        time.sleep(2)

        #build channel list
        stbt.press("KEY_OK")
        time.sleep(2)

        # lock channel 3
        press_key("KEY_DOWN",2)
        stbt.press("KEY_OK")
        time.sleep(1)
        stbt.press("KEY_BACK")
        time.sleep(2)
        
        # clear list
        stbt.press_and_wait("KEY_RIGHT")
        stbt.press("KEY_OK")
        stbt.press_and_wait("KEY_UP")
        stbt.press_and_wait("KEY_OK")
        time.sleep(2)

        # back to settings page
        stbt.press("KEY_BACK")
        time.sleep(3)

    def postcheck(self):
        press_key("KEY_UP",4)
        time.sleep(2)
        press_key("KEY_LEFT",2)
        time.sleep(3)
