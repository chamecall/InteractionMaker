import cv2

class Focuser:
    def __init__(self, batch_size):
        self.batch_size = batch_size
        self.batch = []

    def push_frame(self, frame):
        self.batch.append(frame)

    def get_focus_value(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def get_most_clear_frame(self):
        if len(self.batch) == self.batch_size:
            max_focus_img = max(self.batch, key=self.get_focus_value)
            self.batch = []
            return max_focus_img
        else:
            return None




