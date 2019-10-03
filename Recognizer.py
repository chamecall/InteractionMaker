import time
import matplotlib



#mmcv_image.imshow = imshow
from mmdet.apis import inference_detector, show_result, init_detector


class Recognizer:
    def __init__(self, cfg, weights, threshold=0.9):
        self.cfg = cfg
        self.weights = weights
        self.threshold = threshold
        self.model = init_detector(cfg, weights)


    def inference(self, img):
        result = inference_detector(self.model, img)
        img, label_nums, bboxes = show_result(img, result, self.model.CLASSES, show=False)

        bboxes = [(self.model.CLASSES[label_num], list(map(int, bbox[:-1]))) for label_num, bbox in zip(label_nums, bboxes) if bbox[4] >= self.threshold]
        return img, bboxes

