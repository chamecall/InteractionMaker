import cv2


class VideoReader:
    def __init__(self, video_file_name):
        self.cap = cv2.VideoCapture(video_file_name)
        #self.cap.set(cv2.CAP_PROP_POS_FRAMES, 5020)

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.one_frame_duration = 1000 / self.fps
        self.duration = int(self.frame_count / self.fps)
        self.cur_frame_num = 0
        self.cur_frame = None

    def get_cur_frame(self):
        return self.cur_frame

    def get_next_frame(self):
        read, frame = self.cap.read()
        self.cur_frame = frame
        self.cur_frame_num = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        return self.get_cur_frame()

    def close(self):
        if self.cap:
            self.cap.release()