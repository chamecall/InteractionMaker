from Overlay import Overlay
from ImageProcessing import overlay_image_on_frame


class ImageOverlay(Overlay):
    def __init__(self, media, duration, point, duration_diff):
        super().__init__(media, duration, point, duration_diff)

    def overlay(self, frame):
        overlay_image_on_frame(frame, self.media, self.point)
        return self.dec_duration()


