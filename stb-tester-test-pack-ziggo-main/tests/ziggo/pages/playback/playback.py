import stbt


class PlaybackBar(stbt.FrameObject):
    """The playback bar at the bottom of the screen.

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

    @property
    def is_visible(self) -> bool:
        return bool(self.playhead)

    @property
    def playhead(self) -> stbt.Region:
        return stbt.match("playhead.png", frame=self._frame,
            region=stbt.Region(x=0, y=600, right=1280, bottom=660))

    @property
    def progress(self) -> float:
        """Playhead position, as a percentage in the range 0.0 - 1.0."""
        return (self.playhead.region.x - 70) / (1210 - 70)
