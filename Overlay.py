
class Overlay:
    def __init__(self, media, duration, point, duration_diff):
        self.media = media
        self.duration = duration
        self.duration_step = duration_diff
        self.point = point

    def overlay(self, frame):
        raise NotImplementedError


    def dec_duration(self):
        self.duration -= self.duration_step
        return self.duration > 0
        print('lslslslsls')