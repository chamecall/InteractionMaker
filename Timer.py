
class Timer:
    def __init__(self, duration, step_duration):
        self.duration = duration
        self.step_duration = step_duration


    def ticktock(self):
        self.duration -= self.step_duration
        return self.duration <= 0
