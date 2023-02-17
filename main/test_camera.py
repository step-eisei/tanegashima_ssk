import class_yolo as yolo
import time
import cv2

test = yolo.CornDetect()
image = test.preprocess_image(test.take_photo())
print(image.size)
cv2.imshow("result", image)
cv2.waitKey(0)