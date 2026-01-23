import re

import stbt


class Carousel(stbt.FrameObject):
    """A horizontally-scrolling carousel of movie tiles."""

    COLOR = (0, 140, 244)  # BGR

    @property
    def is_visible(self) -> bool:
        return bool(self.focus)

    @property
    def focus(self):
        """Region of solid orange focus."""
        regions = stbt.find_regions_by_color(
            frame=self._frame,
            color=Carousel.COLOR)
        if len(regions) == 1:
            return regions[0]
        else:
            return None

    @property
    def carousel_name(self):
        region = stbt.Region(x=60, y=self.focus.y - 30,
                             width=800, height=30)
        return stbt.ocr(frame=self._frame, region=region)

    @property
    def text(self):
        """The text in the focused tile."""

        # Find the solid orange part at the bottom by removing the left & right
        # edges around the poster, and then searching for the solid orange
        # colour again.

        # We use a stricter threshold to discard orange parts in the movie
        # poster, so let's make sure we're looking for the exact color of the
        # outline.
        regions = stbt.find_regions_by_color(
            frame=self._frame,
            color=Carousel.COLOR,
            mask=self.focus.extend(x=20, right=-20),
            min_size=(0, 50))
        if len(regions) == 1:
            region = regions[0].extend(x=-15, right=15, y=5)
            return stbt.ocr(frame=self._frame, region=region,
                            tesseract_user_patterns=[r"€\d\*.\d\*"])
        else:
            return None

    @property
    def price(self):
        if self.text:
            m = re.search(r"€\d+\.\d+", self.text)
            if m:
                return m.group()
        return None
