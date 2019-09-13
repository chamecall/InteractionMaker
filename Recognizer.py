import time
import matplotlib



#mmcv_image.imshow = imshow
from mmdet.models import build_detector
from mmdet.apis import inference_detector, show_result, init_detector


class Recognizer:
    def __init__(self, cfg, weights, threshold=0.8):
        self.cfg = cfg
        self.weights = weights
        self.threshold = threshold
        self.model = init_detector(cfg, weights)


    def inference(self, img):
        result = inference_detector(self.model, img)
        img, label_nums, bboxes = show_result(img, result, self.model.CLASSES,
                    score_thr=self.threshold, show=False)
        bboxes = [list(map(int, bbox[:-1])) for bbox in bboxes]
        labels = [self.model.CLASSES[label_num] for label_num in label_nums]
        bboxes = list(zip(labels, bboxes))

        return img, bboxes

