import time

import cv2
import numpy as np
import torch
from numpy import random

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import check_img_size, non_max_suppression, \
    scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized, TracedModel

class CornDetect:
    def __init__(self, source='inference/images', weights='weights/yolov7.pt', conf_thres=0.75, iou_thres=0.45,
           img_size=640, trace=True, project='runs/detect', name='exp',
           device='cpu', augment=False, agnostic_nms=False, classes=None,
           view_img=False, save_txt=False, save_conf=False, nosave=False, save_img=False):
        # Inputs for detection
        self.source = source
        self.weights = weights
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.img_size = img_size
        self.trace = trace
        self.project = project
        self.name = name
        self.device = device
        self.augment = augment
        self.agnostic_nms = agnostic_nms
        self.classes = classes
        self.view_img = view_img
        self.save_txt = save_txt
        self.save_conf = save_conf
        self.nosave = nosave
        self.save_img = save_img

        # Initialize
        self.device = select_device(device)

        # Load model
        self.model = attempt_load(self.weights, map_location=self.device)
        self.stride = int(self.model.stride.max())
        self.img_size = check_img_size(img_size, s=self.stride)
        if trace:
            self.model = TracedModel(self.model, device, img_size)

        # Get names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]

    def take_photo(self):
        camera = cv2.VideoCapture(0)
        success, image = camera.read()
        if not success:
            print("Failed 0n0")
            return -1
        camera.release()
        return image

    def preprocess_image(self, image):
        # Padded resize
        resized_img = letterbox(image, self.img_size, stride=self.stride)[0]

        # Convert
        resized_img = resized_img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        resized_img = np.ascontiguousarray(resized_img)

        resized_img = torch.from_numpy(resized_img).to(self.device)
        resized_img = resized_img.float()  # uint8 to fp16.32
        resized_img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if resized_img.ndimension() == 3:
            resized_img = resized_img.unsqueeze(0)

        return resized_img

    def estimate(self, image):
        # Initialize
        c1, c2 = [-1, -1], [-1, -1]

        t0 = time.time()
        resized_img = self.preprocess_image(image)

        # Inference
        t1 = time_synchronized()
        with torch.no_grad():  # Calculating gradients would cause a GPU memory leak
            pred = self.model(resized_img, augment=self.augment)[0]
        t2 = time_synchronized()

        # Apply NMS
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, classes=self.classes, agnostic=self.agnostic_nms)
        t3 = time_synchronized()

        # Process detections
        det = pred[0]  # May make mistake if there are more than two cones
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(resized_img.shape[2:], det[:, :4], image.shape).round()

            # Write results
            for *xyxy, conf, cls in reversed(det):
                label = f'{self.names[int(cls)]} {conf:.2f}'
                plot_one_box(xyxy, image, label=label, color=self.colors[int(cls)], line_thickness=1)
                c1, c2 = [int(xyxy[0]), int(xyxy[1])], [int(xyxy[2]), int(xyxy[3])]

        # Show result (Just for test)
        # self.show_for_test(image, c1, c2)

        return c1, c2

    def show_for_test(self, image, c1, c2):
        print(c1, c2)
        cv2.imshow("result", image)
        cv2.waitKey(0)

    def image_process(self):
        image = self.take_photo()
        return self.estimate(image)

def main():
    test = CornDetect()
    for i in range(5):
        test.image_process()

if __name__ == "__main__":
    main()
