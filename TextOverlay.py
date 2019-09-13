
from Overlay import Overlay
from ImageProcessing import overlay_text_on_frame


class TextOverlay(Overlay):
    def __init__(self, media, duration, point, duration_diff):
        super().__init__(media, duration, point, duration_diff)

    def overlay(self, frame):
        overlay_text_on_frame(frame, self.media, self.point)
        return self.dec_duration()


