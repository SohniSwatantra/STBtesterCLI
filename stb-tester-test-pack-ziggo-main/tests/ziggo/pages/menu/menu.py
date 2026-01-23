import random
import time
import stbt
from tests.remote_control import press_key_and_wait

from tests import helper

class Menu(stbt.FrameObject):
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

    region = stbt.Region(x=0, y=0, width=1280, bottom=180)

    @staticmethod
    def launch() -> "Menu":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        for _ in range(6):
            stbt.press("KEY_BACK", interpress_delay_secs=1)
        assert stbt.wait_until(lambda: not Menu(), stable_secs=2)
        stbt.press("KEY_MENU")
        page = stbt.wait_until(Menu)
        assert page, "Failed to launch Menu"
        return page  

    @property
    def is_visible(self) -> bool:
        return bool(self.orange_underline)

    @property
    def focus(self):
        return stbt.ocr(
            region=self.orange_underline.above(height=40).extend(bottom=-10),
            frame=self._frame,
            engine=stbt.OcrEngine.LSTM)
        
    @property
    def orange_underline(self):
        regions = stbt.find_regions_by_color(
            frame=self._frame,
            color=(16, 135, 225),
            mask=self.region,
            min_size=(50, 3),
            max_size=(300, 8))
        if len(regions) == 1:
            return regions[0]
        else:
            return None

    def navigate_to(self, target: str) -> "Menu":
        page = self
        assert page, "Not at Menu page"
        for _ in range(10):
            if page.focus == target:
                return page
            assert stbt.press_and_wait("KEY_RIGHT", region=self.region)
            page = page.refresh()
        assert False, "Didn't find target %r in 10 iterations" % (target,)

    def select(self, *target: str):
        page = self
        while target:
            page.navigate_to(target[0])
            assert stbt.press_and_wait("KEY_OK", region=self.region)
            target = target[1:]
            if target:
                page = stbt.wait_until(Menu)


    def perform_zapping(self):
        """
        performs zapping on the box, with channel+/channel-,
        numeric channel press and wrong LCN
        """
        # check with Numeric channel
        key = random.choice([*range(1,10)])
        key_to_press = f'KEY_{key}'

        stbt.press_and_wait(key_to_press)
        time.sleep(2)
        
        #press channel +
        press_key_and_wait("KEY_CHANNELUP", 3)
        time.sleep(3)

        #press channel -
        press_key_and_wait("KEY_CHANNELDOWN", 3)
        time.sleep(3)

        # for wrong LCN
        stbt.press("KEY_2")
        stbt.press("KEY_5")
        stbt.press("KEY_1")
        time.sleep(5)

    def navigate_to_watchlist(self):
        helper.back_to_top(is_watchlist = True)
