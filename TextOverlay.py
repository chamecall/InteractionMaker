
from Overlay import Overlay
from ImageProcessing import overlay_text_on_frame


class TextOverlay(Overlay):
    def __init__(self, media, duration, delay, coords, duration_diff):
        super().__init__(media, duration, delay, coords, duration_diff)

    def overlay(self, frame):
        if self.dec_delay():
            return True
        overlay_text_on_frame(frame, *self.media, self.coords)
        return self.dec_duration()


