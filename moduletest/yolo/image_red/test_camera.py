import cv2
bgr = [0, 25, 0]
camera = cv2.VideoCapture(0)
success, img = camera.read()
if not success: 
	print('0n0')
else:
    if(bgr != [0, 0, 0]):
        for i in range(len(img)):
            for j in range(len(img[0])):
                bgr[i, j] = [img[i, j, k]+bgr[k] for k in range(3)]
	print(img.shape)
	cv2.imshow('img', img)
	cv2.waitKey(0)

