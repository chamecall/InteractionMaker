import cv2
import imutils

class SceneSegmentator:
    def __init__(self, batch_size, min_thresh=30.0, max_thresh=33.0):
        self.batch_size = int(batch_size)
        self.batch = []
        self.min_thresh = min_thresh
        self.max_thresh = max_thresh
        self.subtractor = cv2.bgsegm.createBackgroundSubtractorGMG()
        self.captured = self.new_scene_frame_extracted = False

    def push_frame(self, frame):
        self.check_new_scene(frame)
        self.batch.append(frame)

    def get_focus_value(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = imutils.resize(gray, width=600)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def get_most_clear_frame(self):
        if len(self.batch) == self.batch_size or self.new_scene_frame_extracted:
            max_focus_img = max(self.batch, key=self.get_focus_value)

            self.batch = []
            self.new_scene_frame_extracted = False
            return max_focus_img
        else:
            return None

    def check_new_scene(self, frame):
        frame = imutils.resize(frame, width=600)
        mask = self.subtractor.apply(frame)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        H, W = mask.shape[:2]
        p = int((cv2.countNonZero(mask) / float(W * H)) * 100)

        if p < self.min_thresh and not self.captured:
            self.captured = self.new_scene_frame_extracted = True
            self.batch = []
        elif self.captured and p >= self.max_thresh:
            self.captured = False

