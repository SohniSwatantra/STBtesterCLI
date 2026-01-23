import stbt


class Button(stbt.FrameObject):
    """A focused orange button anywhere on the screen."""

    @property
    def is_visible(self) -> bool:
        return bool(self.focus)

    @property
    def focus(self):
        regions = stbt.find_regions_by_color(
            frame=self._frame,
            color=(16, 135, 225))
        if len(regions) == 1:
            return regions[0]
        else:
            return None

    @property
    def text(self) -> str:
        # Read the text inside the button. Exclude the edges & corners.
        return stbt.ocr(
            region=self.focus.erode(10),
            frame=self._frame)
