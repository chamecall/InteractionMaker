from Overlay import Overlay
from ImageProcessing import overlay_image_on_frame_by_box, overlay_image_on_frame_by_center_point


class ImageOverlay(Overlay):
    def __init__(self, media, duration, delay, coords, duration_diff):
        super().__init__(media, duration, delay, coords, duration_diff)

    def overlay(self, frame):
        if self.dec_delay():
            return True
        if len(self.coords) == 4:
            overlay_image_on_frame_by_box(frame, self.media, self.coords)
        elif len(self.coords) == 2:
            overlay_image_on_frame_by_center_point(frame, self.media, self.coords)
        return self.dec_duration()


