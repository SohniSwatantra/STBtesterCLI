import stbt


class MenuTest(stbt.FrameObject):
    """Main Menu.

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

    region = stbt.Region(x=114, y=28, width=990, height=47)

    @staticmethod
    def launch() -> "MenuTest":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        stbt.press("KEY_BACK")
        stbt.press("KEY_BACK")
        stbt.press("KEY_BACK")
        stbt.press("KEY_BACK")
        stbt.press("KEY_1")
        stbt.press("KEY_MENU")
        page = stbt.wait_until(MenuTest)
        assert page, "Failed to launch Menu"
        return page

    @property
    def is_visible(self) -> bool:
        return self.selection in ("TV & REPLAY", "TV APPS", "MOVIES & SERIES",
                                  "RECORDINGS")

    @property
    def selection(self):
        return stbt.ocr(region=self.region,
                        frame=self._frame,
                        text_color=(255, 255, 255), text_color_threshold=50)

    def navigate_to(self, target: str) -> "MenuTest":
        page = self
        for _ in range(10):
            if page.selection == target:
                return page
            assert stbt.press_and_wait("KEY_RIGHT", region=self.region)
            page = page.refresh()
        assert False, "Didn't find target %r in 10 iterations" % (target,)
