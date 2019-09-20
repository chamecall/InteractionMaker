import json


class DetectionReader:
    def __init__(self, json_file):
        self.json_data = open(json_file)
        self.detections = json.load(self.json_data)

    def get_detections_per_specified_frame(self, frame_num):
        return self.detections[str(frame_num)]

    def close(self):
        self.json_data.close()

