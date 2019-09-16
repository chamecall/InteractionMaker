
class Overlay:
    def __init__(self, media, duration, delay, coords: tuple, duration_diff):
        self.media = media
        self.duration = duration
        self.duration_step = duration_diff
        self.coords = coords
        self.delay = delay

    def overlay(self, frame):
        raise NotImplementedError


    def dec_duration(self):
        self.duration -= self.duration_step
        return self.duration > 0

    def set_coords(self, coords):
        self.coords = coords

    def dec_delay(self):
        self.delay -= self.duration_step
        print(self.delay)
        return self.delay > 0