import random
import stbt

from tests.remote_control import press_key


class Apps(stbt.FrameObject):
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

    region = stbt.Region(x=48, y=478, width=662, height=43)

    @staticmethod
    def launch() -> "Apps":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        page = Apps()
        if page:
            # We're already on this page, no work to do.
            return page

        # TODO: Implement navigation to get to this screen:
        assert stbt.press_and_wait("KEY_OK")
        page = stbt.wait_until(Apps)
        assert page, "Failed to launch Apps"
        return page

    @property
    def is_visible(self) -> bool:
        # TODO: Add apps.png to this directory. This should be an image of the
        # screen that this class is supposed to match. You can ignore dynamic
        # regions of the screen by making them transparent.
        return stbt.match("TV Apps.png", frame=self._frame)

    @property
    def selection(self):
        # This is just an example. Note how we pass self._frame to all our image
        # processing functions.
        #
        # TODO: Adapt this property to your page or delete it.
        return stbt.ocr(region=self.region,
                        frame=self._frame,
                        text_color=(255, 255, 255), text_color_threshold=50)

    def navigate_to(self, target: str) -> "str":
        page = self
        for _ in range(10):
            if page.selection == target:
                return page
            stbt.press_and_wait("KEY_DOWN", region=self.region)
            page = page.refresh()
        assert False, "Didn't find target %r in 10 iterations" % (target,)

    def navigate_appstore(self):
        # stbt.press_and_wait("KEY_RIGHT")
        stbt.press('KEY_DOWN')
        press_key("KEY_RIGHT", random.randint(2,9))
        stbt.press_and_wait("KEY_OK")
        
