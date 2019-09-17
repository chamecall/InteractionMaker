
from Overlay import Overlay
from ImageProcessing import overlay_text_on_frame


class TextOverlay(Overlay):
    def __init__(self, media, duration, coords, duration_diff):
        super().__init__(media, duration, coords, duration_diff)

    def overlay(self, frame):
        overlay_text_on_frame(frame, *self.media, self.coords)
        return self.dec_duration()


