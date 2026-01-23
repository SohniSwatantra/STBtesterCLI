import time
import stbt

from tests.remote_control import press_key, press_key_and_wait


class Profile(stbt.FrameObject):
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
    def launch() -> "Profile":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        page = Profile()
        if page:
            # We're already on this page, no work to do.
            return page

        # TODO: Implement navigation to get to this screen:
        assert stbt.press_and_wait("KEY_???")
        page = stbt.wait_until(Profile)
        assert page, "Failed to launch Profile"
        return page

    @property
    def is_visible(self) -> bool:
        # TODO: Add profile.png to this directory. This should be an image of
        # the screen that this class is supposed to match. You can ignore
        # dynamic regions of the screen by making them transparent.
        return stbt.match("profile.png", frame=self._frame)

    def check_profile(self):
        stbt.press("KEY_LEFT", interpress_delay_secs=2)
        stbt.press("KEY_OK", interpress_delay_secs=2)
        time.sleep(1)

        #enter name
        press_key("KEY_OK",3)
        stbt.press_and_wait("KEY_BACK")

        # skip preferences
        for i in range (3):
            no_of_times = 3 if i ==2 else 1
            press_key("KEY_DOWN", no_of_times)
            stbt.press("KEY_OK", interpress_delay_secs=2)

        time.sleep(5)

        # delete the profile
        for _ in range(3):
            stbt.press_and_wait("KEY_DOWN")
            stbt.press("KEY_OK", interpress_delay_secs=2)

        stbt.press_and_wait("KEY_UP")
        stbt.press("KEY_OK", interpress_delay_secs=2)
        time.sleep(5)

    def delete_profile(self):
        # stbt.press_and_wait("KEY_BACK")
        time.sleep(5)
        stbt.press("KEY_BACK")
        time.sleep(2)
        press_key("KEY_DOWN", 2)
        time.sleep(1)
        stbt.press_and_wait("KEY_OK")
        stbt.press("KEY_UP")
        stbt.press_and_wait("KEY_OK")
        stbt.press("KEY_UP")




        