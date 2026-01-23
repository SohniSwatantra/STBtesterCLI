from operator import contains
import stbt
from tests import helper

from tests.remote_control import *
from tests.ziggo.pages.button.button import Button
from tests.helper import perform_video_tricks, watch_or_continue_watch_video
from tests.ziggo.pages.carousel.carousel import Carousel
from tests.ziggo.pages.menu.menu import Menu


class MoviesAndSeries(stbt.FrameObject):
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
    region = stbt.Region(x=0, y=0, width=1280, bottom=180)
 
    @staticmethod
    def launch() -> "MoviesAndSeries":
        # This function should navigate to this screen from any state, returning
        # an instance of this class, or raising an exception if that is not
        # possible. You may add arguments to this method.
        #
        # This method may not be applicable for all Page Objects, in which case
        # you can delete it.

        page = MoviesAndSeries()
        if page:
            # We're already on this page, no work to do.
            return page

        # TODO: Implement navigation to get to this screen:
        assert stbt.press_and_wait("KEY_ONDEMAND")
        page = stbt.wait_until(MoviesAndSeries)
        assert page, "Failed to launch MoviesAndSeries"
        return page

    @property
    def is_visible(self) -> bool:
        # This should be an image of the screen that 
        # this class is supposed to match. You can
        # ignore dynamic regions of the screen by making them transparent.
        return stbt.match("moviesandseries.png", frame=self._frame)
    
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

    def navigate_to(self, target: str):
        page = self
        assert page, "Not at Menu page"
        for _ in range(10):
            if page.focus == target:
                return page
            assert stbt.press_and_wait(key="KEY_RIGHT", region=self.region)
            page = page.refresh()
        assert False, "Didn't find target %r in 10 iterations" % (target,)

    def watch_trailer(self): 
        """
        Watch Trailer for a movie
        """
        # is_info = stbt.ocr(region=stbt.Region(x=55, y=27, width=91, height=36)) == 'INFO'
        stbt.press_and_wait("KEY_DOWN")
        # tile = Carousel()
        # if tile.carousel_name == 'Trailer': 
        stbt.press_and_wait('KEY_OK')
        watch_or_continue_watch_video()
        stbt.press_and_wait("KEY_BACK")

    def add_to_watchlist(self):
        """
        add asset to watchlist
        """
        stbt.press_and_wait("KEY_RIGHT")
        time.sleep(3)
        stbt.press_and_wait("KEY_OK")
        # if stbt.ocr(region=stbt.Region(x=211, y=560, width=301, height=56)) == '69 ADD TO WATCHLIST':
        #     assert stbt.press_and_wait("KEY_OK")
        # assert True, 'Already added to watchlist'


    def check_sections(self, section_name):
        """
        navigates to various sections of Movies and Series 
        and plays VOD and performs Tricks
        """
        stbt.press_and_wait("KEY_RIGHT")
        time.sleep(2)
        self.check_genre(section_name)

        helper.back_to_top(is_vod=True)
        down_key_press_count = 0
        for _ in range(10):
            stbt.press_and_wait("KEY_DOWN")
            page = Carousel()
            if page.carousel_name == "Recently added":
                if page.text == "More":
                    stbt.press_and_wait("KEY_OK")
                    down_key_press_count = _
                    break
        # no_of_times = {'Movies': 2,
        #                'Series': 5,
        #                'Kids': 2,
        #                'Rent': 2}

        # if section_name in ['Movies', 'Series', 'Kids']:
        #     stbt.press('KEY_RIGHT', interpress_delay_secs=2)
        #     press_key_and_wait("KEY_OK", no_of_times[section_name])
        #     watch_or_continue_watch_video()
        #     perform_video_tricks()
                    
        for _ in range(10):
            assert stbt.press("KEY_BACK", interpress_delay_secs=2)
            time.sleep(2)
            if stbt.match('moviesAndSeriesTab.png',
                           region=stbt.Region(x=60, y=37, width=165, height=25)):
                assert True, 'Movies And Series screen'
                break
            elif stbt.match('mainMenu_moviesandSeriesGrid.png',region=stbt.Region(x=672, y=78, width=189, height=2)):
                stbt.press_and_wait("KEY_OK")


        no_of_times = down_key_press_count + 1
        press_key("KEY_UP", no_of_times)

    def check_genre(self, section_name):
        """
        navigates to various sections of Movies and Series 
        and plays VOD and performs Tricks
        """
        if(section_name == "Movies" or section_name == "Series"):
            press_key("KEY_DOWN", 2)
        elif(section_name == "Kids"):
            press_key("KEY_DOWN", 1)
        elif(section_name == "Rent"):
            press_key("KEY_DOWN", 3)

        for _ in range(15):
            stbt.press_and_wait("KEY_RIGHT")


    def check_providers(self):
        """
        navigates through the Providers section of Movies and series screen
        """
        stbt.press_and_wait("KEY_RIGHT")
        stbt.press_and_wait("KEY_DOWN", region=stbt.Region(x=55, y=80, width=902, height=246))
        stbt.press_and_wait("KEY_OK")
        helper.back_to_top('Providers')


    def play_vod(self):
        """
        Parent method that should be called to check all the sections
        under movies and series screen
        """
        self.check_sections('Movies')
        self.check_sections('Series')
        self.check_sections('Kids')
        self.check_sections('Rent')
        self.check_providers()
