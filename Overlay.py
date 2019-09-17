
class Overlay:
    def __init__(self, media, duration, coords: tuple, duration_diff):
        self.media = media
        self.duration = duration
        self.duration_step = duration_diff
        self.coords = coords

    def overlay(self, frame):
        raise NotImplementedError


    def dec_duration(self):
        self.duration -= self.duration_step
        return self.duration > 0

    def set_coords(self, coords):
        self.coords = coords

