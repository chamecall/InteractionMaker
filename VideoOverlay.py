import cv2

from Overlay import Overlay
from ImageProcessing import overlay_img_in_top_right_frame_corner

class VideoOverlay(Overlay):
    def __init__(self, cap: cv2.VideoCapture, duration, coords, duration_diff):
        super().__init__(cap, duration, coords, duration_diff)
        self.fps = self.media.get(cv2.CAP_PROP_FPS)
        self.frames_num = int(self.fps * duration / 1000)

    def overlay(self, frame):
        captured, inner_frame = self.media.read()
        if not captured:
            return False

        overlay_img_in_top_right_frame_corner(frame, inner_frame, self.coords)
        return self.dec_duration()

    def dec_duration(self):
        self.frames_num -= 1
        return self.frames_num > 0
