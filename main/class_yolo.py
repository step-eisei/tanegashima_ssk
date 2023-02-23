import sys
sys.path.append("/home/pi/tanegashima_ssk/main/yolov7/")

import cv2
import numpy as np
import torch
from numpy import random

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import check_img_size, non_max_suppression, \
    scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device, TracedModel


# Take photo
def take_photo():
    camera = cv2.VideoCapture(0)
    success, image = camera.read()
    if not success:
        print("Failed 0n0")
        return -1
    image = cv2.flip(image, -1)
    camera.release()
    return image

# Adjust brightness and contrast
def automatic_brightness_and_contrast(image, clip_hist_percent=25):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = [float(hist[0])]
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return auto_result, alpha, beta

class CornDetect:
    def __init__(self, weights='/home/pi/tanegashima_ssk/main/yolov7/weights/best.pt', conf_thres=0.25, iou_thres=0.45, save_img=True,
                 img_size=640, trace=True, device='cpu', augment=False, agnostic_nms=False, classes=None):
        # Inputs for detection
        self.weights = weights
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.save_img = save_img
        self.img_size = img_size
        self.device = device
        self.augment = augment
        self.agnostic_nms = agnostic_nms
        self.classes = classes

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
        self.count = 0

    # Preprocess image (not important)
    def preprocess_image(self, image):
        # Adjust brightness and contrast
        resized_img, _, _ = automatic_brightness_and_contrast(image)

        # Padded resize
        resized_img = letterbox(resized_img, self.img_size, stride=self.stride)[0]

        # Convert
        resized_img = resized_img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        resized_img = np.ascontiguousarray(resized_img)

        resized_img = torch.from_numpy(resized_img).to(self.device)
        resized_img = resized_img.float()  # uint8 to fp16.32
        resized_img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if resized_img.ndimension() == 3:
            resized_img = resized_img.unsqueeze(0)

        return resized_img

    # Start to estimate
    def estimate(self, image):
        # Initialize
        c1, c2 = [-1, -1], [-1, -1]
        resized_img = self.preprocess_image(image)

        # Inference
        with torch.no_grad():  # Calculating gradients would cause a GPU memory leak
            pred = self.model(resized_img, augment=self.augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres,
                                   classes=self.classes, agnostic=self.agnostic_nms)

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

        return c1, c2, image

    # Save both original image and adjusted image
    def save_image(self, image):
        self.count += 1
        adjusted_image, _, _ = automatic_brightness_and_contrast(image)
        cv2.imwrite(f'camera/image{self.count}.jpg', image)
        cv2.imwrite(f'camera/adjusted_image{self.count}.jpg', adjusted_image)

    # Use it in the main program
    def image_process(self):
        image = take_photo()
        return self.estimate(image)


if __name__ == "__main__":
    def main():
        test = CornDetect()
        while True:
            image = take_photo()
            c1, c2, estimated_image = test.estimate(image)
            adjusted_image, _, _ = automatic_brightness_and_contrast(estimated_image)
            print(c1, c2)

            cv2.imshow('estimated image', estimated_image)
            cv2.imshow('adjusted image', adjusted_image)

            key = cv2.waitKey(0)
            if key == ord('q'):
                break
    main()
