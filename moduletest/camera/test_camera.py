import cv2
import numpy as np
import time
from matplotlib import pyplot as plt
import sys

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

    
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return auto_result, alpha, beta

alpha = 1.0
beta = 0.0
if len(sys.argv) == 3:
      alpha = float(sys.argv[1])
      beta = float(sys.argv[2])
camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
print(cv2.CAP_PROP_AUTO_EXPOSURE)
#camera.set(cv2.CAP_PROP_AUTO_WB, 1)
camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
success, image = camera.read()
image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
#image, _, _ = automatic_brightness_and_contrast(image)
if not success:
    print("failed")
else:
    cv2.imwrite("test.jpg", image)
    print(image.shape)
while True: 
	
    success, image = camera.read()
    if not success:
        print('failed 0n0')
        break
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    #image, _, _ = automatic_brightness_and_contrast(image)
    cv2.imshow('image', image)
    key = cv2.waitKey(1)
    if key == ord('q'): 
        break
              
cv2.destroyWindow('image')
success, image = camera.read()
#image = cv2.convertScaleAbs(image, alpha=1.0, beta=-50)
#image, _, _ = automatic_brightness_and_contrast(image)
if not success:
      print("failed")
else:
      cv2.imwrite("test_after.jpg", image)
      print(image.shape)

camera.release()
	
