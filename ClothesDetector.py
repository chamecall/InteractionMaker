from __future__ import division

from yolo.utils.models import *
from yolo.utils.utils import *
from yolo.utils.datasets import *
from yolo.utils.utils2 import *
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable

import matplotlib.pyplot as plt
import cv2
import sys

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ClothesDetector:
    def __init__(self, conf_path, weights_path, classes_path, prob_thresh=0.25, nms_thresh=0.3, img_size=416):
        params = {"model_def": conf_path,
                  "weights_path": weights_path,
                  "img_size": img_size,
                  "device": device
                  }

        self.prob_thresh = prob_thresh
        self.nms_thresh = nms_thresh
        self.classes = load_classes(classes_path)
        self.Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor
        self.img_size = img_size
        cmap = plt.get_cmap("tab20")
        self.colors = np.array([cmap(i) for i in np.linspace(0, 1, 20)])
        np.random.shuffle(self.colors)
        self.model = load_model(params)
        print('Model loaded successfully.')


    def detect_clothes(self, img):
        x, _, _ = cv_img_to_tensor(img)
        x.to(device)

        with torch.no_grad():
            input_img = Variable(x.type(self.Tensor))
            detections = self.model(input_img)
            detections = non_max_suppression(detections, self.prob_thresh, self.nms_thresh)
        clothes_detections = []

        if detections[0] is not None:

            detections_org = detections[0].clone()
            detections = rescale_boxes(detections[0], self.img_size, img.shape[:2])
            unique_labels = detections[:, -1].cpu().unique()
            for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:

                prob = int(cls_conf.item() * 100)
                label = self.classes[int(cls_pred)]
                #print('Label:', label)
                clothes_detections.append([label, ((x1, y1), (x2, y2)), prob])

        return clothes_detections


